# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask

__plugin_name__ = "Octo Fire Guard"
__plugin_pythoncompat__ = ">=3.8,<4"


class OctoFireGuardPlugin(octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.StartupPlugin,
                          octoprint.plugin.SimpleApiPlugin):

    def __init__(self):
        self._hotend_threshold_exceeded = False
        self._heatbed_threshold_exceeded = False
        self._last_temperatures = {}

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            hotend_threshold=250,  # Default hotend threshold in °C
            heatbed_threshold=100,  # Default heatbed threshold in °C
            termination_mode="gcode",  # Options: "gcode" or "psu"
            termination_gcode="M112\nM104 S0\nM140 S0",  # Emergency stop + turn off heaters
            psu_plugin_name="psucontrol",  # Name of PSU control plugin
            enable_monitoring=True,  # Enable/disable monitoring
            check_interval=1  # Check interval in seconds (not currently used, uses temperature callback)
        )

    def get_settings_version(self):
        return 1

    ##~~ AssetPlugin mixin

    def get_assets(self):
        return dict(
            js=["js/octo_fire_guard.js"],
            css=["css/octo_fire_guard.css"]
        )

    ##~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False),
            dict(type="generic", template="octo_fire_guard_alert_modal.jinja2", custom_bindings=False)
        ]

    ##~~ StartupPlugin mixin

    def on_after_startup(self):
        self._logger.debug("Initializing Octo Fire Guard plugin")
        self._logger.info("Octo Fire Guard plugin started")
        self._logger.info("Hotend threshold: {}°C".format(self._settings.get(["hotend_threshold"])))
        self._logger.info("Heatbed threshold: {}°C".format(self._settings.get(["heatbed_threshold"])))
        self._logger.info("Termination mode: {}".format(self._settings.get(["termination_mode"])))
        self._logger.debug("Monitoring enabled: {}".format(self._settings.get_boolean(["enable_monitoring"])))
        self._logger.debug("Plugin initialization complete")

    ##~~ SimpleApiPlugin mixin

    def get_api_commands(self):
        return dict(
            test_alert=[]
        )

    def on_api_command(self, command, data):
        if command == "test_alert":
            self._logger.info("Testing alert system")
            self._plugin_manager.send_plugin_message(
                self._identifier,
                dict(
                    type="temperature_alert",
                    sensor="test",
                    current_temp=999,
                    threshold=250,
                    message="This is a test alert"
                )
            )
            return flask.jsonify(success=True)

    def is_api_protected(self):
        """
        Explicitly declare API protection status.
        Returns True to require authentication for API commands.
        """
        return True

    ##~~ Temperature callback

    def temperature_callback(self, comm, parsed_temperatures):
        """
        Called when temperature data is received from the printer.
        This is where we monitor temperatures and trigger alerts.
        """
        self._logger.debug("temperature_callback invoked - processing temperature data")
        
        if not self._settings.get_boolean(["enable_monitoring"]):
            self._logger.debug("Monitoring is disabled, skipping temperature checks")
            return parsed_temperatures

        self._logger.debug("Monitoring is enabled, checking temperatures")
        self._logger.debug("Received parsed_temperatures: {}".format(parsed_temperatures))
        
        hotend_threshold = self._settings.get_float(["hotend_threshold"])
        heatbed_threshold = self._settings.get_float(["heatbed_threshold"])
        self._logger.debug("Current thresholds - Hotend: {}°C, Heatbed: {}°C".format(
            hotend_threshold, heatbed_threshold
        ))

        # Check hotend temperature (tool0, tool1, etc. or T0, T1, etc.)
        for tool_key in parsed_temperatures:
            # Support both old format (tool0, tool1) and new format (T0, T1)
            # For new format: starts with 'T', has at least one more character, and all chars after 'T' are digits
            is_new_format_tool = (tool_key.startswith("T") and len(tool_key) >= 2 and 
                                  tool_key[1:].isdigit() and len(tool_key[1:]) > 0)
            if tool_key.startswith("tool") or is_new_format_tool:
                self._logger.debug("Checking hotend temperature for {}".format(tool_key))
                temp_data = parsed_temperatures[tool_key]
                if isinstance(temp_data, tuple) and len(temp_data) >= 2:
                    current_temp = temp_data[0]
                    self._logger.debug("{} current temperature: {}°C".format(tool_key, current_temp))
                    if current_temp is not None and current_temp > hotend_threshold:
                        self._logger.debug("{} temperature {} exceeds threshold {}".format(
                            tool_key, current_temp, hotend_threshold
                        ))
                        if not self._hotend_threshold_exceeded:
                            self._logger.debug("Hotend threshold flag not yet set, triggering alert")
                            self._logger.warning(
                                "HOTEND TEMPERATURE ALERT! Current: {}°C, Threshold: {}°C".format(
                                    current_temp, hotend_threshold
                                )
                            )
                            self._trigger_emergency_shutdown("hotend", current_temp, hotend_threshold)
                            self._hotend_threshold_exceeded = True
                            self._logger.debug("Hotend threshold exceeded flag set to True")
                        else:
                            self._logger.debug("Hotend threshold already exceeded, skipping duplicate alert")
                    elif current_temp is not None and current_temp <= hotend_threshold - 10:
                        # Reset flag if temperature drops significantly below threshold
                        if self._hotend_threshold_exceeded:
                            self._logger.debug("Hotend temperature dropped to {}°C, resetting threshold flag".format(
                                current_temp
                            ))
                            self._hotend_threshold_exceeded = False
                            self._logger.debug("Hotend threshold exceeded flag reset to False")

        # Check heatbed temperature (support both "bed" and "B" formats)
        bed_key = None
        if "bed" in parsed_temperatures:
            bed_key = "bed"
        elif "B" in parsed_temperatures:
            bed_key = "B"
        
        if bed_key:
            self._logger.debug("Checking heatbed temperature")
            temp_data = parsed_temperatures[bed_key]
            if isinstance(temp_data, tuple) and len(temp_data) >= 2:
                current_temp = temp_data[0]
                self._logger.debug("Heatbed current temperature: {}°C".format(current_temp))
                if current_temp is not None and current_temp > heatbed_threshold:
                    self._logger.debug("Heatbed temperature {} exceeds threshold {}".format(
                        current_temp, heatbed_threshold
                    ))
                    if not self._heatbed_threshold_exceeded:
                        self._logger.debug("Heatbed threshold flag not yet set, triggering alert")
                        self._logger.warning(
                            "HEATBED TEMPERATURE ALERT! Current: {}°C, Threshold: {}°C".format(
                                current_temp, heatbed_threshold
                            )
                        )
                        self._trigger_emergency_shutdown("heatbed", current_temp, heatbed_threshold)
                        self._heatbed_threshold_exceeded = True
                        self._logger.debug("Heatbed threshold exceeded flag set to True")
                    else:
                        self._logger.debug("Heatbed threshold already exceeded, skipping duplicate alert")
                elif current_temp is not None and current_temp <= heatbed_threshold - 10:
                    # Reset flag if temperature drops significantly below threshold
                    if self._heatbed_threshold_exceeded:
                        self._logger.debug("Heatbed temperature dropped to {}°C, resetting threshold flag".format(
                            current_temp
                        ))
                        self._heatbed_threshold_exceeded = False
                        self._logger.debug("Heatbed threshold exceeded flag reset to False")

        self._logger.debug("temperature_callback complete, returning parsed_temperatures")
        return parsed_temperatures

    def _trigger_emergency_shutdown(self, sensor_type, current_temp, threshold):
        """
        Trigger emergency shutdown when temperature threshold is exceeded.
        """
        self._logger.debug("_trigger_emergency_shutdown called for {} - temp: {}, threshold: {}".format(
            sensor_type, current_temp, threshold
        ))
        self._logger.error(
            "EMERGENCY SHUTDOWN TRIGGERED! {} temperature {} exceeded threshold {}".format(
                sensor_type.upper(), current_temp, threshold
            )
        )

        # Send alert to frontend
        self._logger.debug("Sending temperature alert to frontend")
        self._plugin_manager.send_plugin_message(
            self._identifier,
            dict(
                type="temperature_alert",
                sensor=sensor_type,
                current_temp=current_temp,
                threshold=threshold,
                message="EMERGENCY: {} temperature ({:.1f}°C) exceeded threshold ({:.1f}°C)!".format(
                    sensor_type.upper(), current_temp, threshold
                )
            )
        )

        # Execute termination command
        termination_mode = self._settings.get(["termination_mode"])
        self._logger.debug("Executing termination mode: {}".format(termination_mode))

        if termination_mode == "gcode":
            self._execute_gcode_termination()
        elif termination_mode == "psu":
            self._execute_psu_termination()
        else:
            self._logger.error("Unknown termination mode: {}".format(termination_mode))

    def _execute_gcode_termination(self):
        """
        Execute GCode termination commands.
        """
        termination_gcode = self._settings.get(["termination_gcode"])
        self._logger.debug("_execute_gcode_termination called")
        self._logger.info("Executing GCode termination: {}".format(termination_gcode))

        # Split by newlines and send each command
        if termination_gcode:
            commands = termination_gcode.split("\n")
            self._logger.debug("Termination GCode split into {} commands".format(len(commands)))
            for command in commands:
                command = command.strip()
                if command:
                    self._logger.info("Sending emergency GCode: {}".format(command))
                    self._printer.commands(command)
        self._logger.debug("GCode termination complete")

    def _execute_psu_termination(self):
        """
        Execute PSU control termination (turn off power).
        """
        psu_plugin_name = self._settings.get(["psu_plugin_name"])
        self._logger.debug("_execute_psu_termination called")
        self._logger.info("Attempting to turn off PSU via plugin: {}".format(psu_plugin_name))

        # Try to send turn off command via PSU control plugin
        try:
            # First, try to turn off heaters with GCode
            self._logger.debug("Turning off heaters before PSU shutdown")
            self._printer.commands("M104 S0")  # Turn off hotend
            self._printer.commands("M140 S0")  # Turn off bed

            # Try to access PSU control plugin and call its turn_psu_off method
            self._logger.debug("Looking up PSU plugin: {}".format(psu_plugin_name))
            psu_plugin = self._plugin_manager.get_plugin_info(psu_plugin_name)
            if psu_plugin and psu_plugin.implementation:
                self._logger.debug("PSU plugin found, checking for turn off methods")
                # Try different methods that PSU control plugins might use
                if hasattr(psu_plugin.implementation, 'turn_psu_off'):
                    self._logger.info("Calling turn_psu_off method")
                    psu_plugin.implementation.turn_psu_off()
                elif hasattr(psu_plugin.implementation, 'turnPSUOff'):
                    self._logger.info("Calling turnPSUOff method")
                    psu_plugin.implementation.turnPSUOff()
                else:
                    self._logger.warning("PSU plugin found but no turn off method available")
                    raise Exception("No turn off method found in PSU plugin")
                
                self._logger.info("PSU shutdown command sent successfully")
            else:
                self._logger.error("PSU control plugin '{}' not found or not loaded".format(psu_plugin_name))
                raise Exception("PSU plugin not found")
                
        except Exception as e:
            self._logger.error("Failed to execute PSU termination: {}".format(str(e)))
            # Fallback to GCode termination
            self._logger.warning("Falling back to GCode termination")
            self._execute_gcode_termination()
        
        self._logger.debug("PSU termination process complete")

    ##~~ Softwareupdate hook

    def get_update_information(self):
        return dict(
            octo_fire_guard=dict(
                displayName="Octo Fire Guard",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="rdar-lab",
                repo="octo-fire-guard",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/rdar-lab/octo-fire-guard/archive/{target_version}.zip"
            )
        )


__plugin_implementation__ = OctoFireGuardPlugin()


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoFireGuardPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.temperatures.received": __plugin_implementation__.temperature_callback
    }
