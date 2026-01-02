# coding=utf-8
"""
Comprehensive unit tests for Octo Fire Guard plugin.
Tests all major functionality including temperature monitoring,
emergency shutdown, and alert systems.
"""

from __future__ import absolute_import
import unittest
from unittest.mock import Mock, MagicMock, patch, call, PropertyMock
import sys
import os

# Before importing anything, we need to mock the OctoPrint dependencies
# We'll patch them at import time to avoid metaclass conflicts

# Create a module-level mock for octoprint
class FakeOctoprint:
    class plugin:
        class SettingsPlugin:
            pass
        
        class AssetPlugin:
            pass
        
        class TemplatePlugin:
            pass
        
        class StartupPlugin:
            pass
        
        class SimpleApiPlugin:
            pass
        
        class ShutdownPlugin:
            pass
    
    class util:
        class RepeatedTimer:
            def __init__(self, interval, function):
                self.interval = interval
                self.function = function
                self.is_running = False
            
            def start(self):
                self.is_running = True
            
            def cancel(self):
                self.is_running = False

# Mock flask module
class FakeFlask:
    @staticmethod
    def jsonify(**kwargs):
        return kwargs

# Install the mocks
sys.modules['octoprint'] = FakeOctoprint()
sys.modules['octoprint.plugin'] = FakeOctoprint.plugin
sys.modules['octoprint.util'] = FakeOctoprint.util
sys.modules['flask'] = FakeFlask()

# Add parent directory to path to import the plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Now we can import the plugin
from octoprint_octo_fire_guard import OctoFireGuardPlugin


class TestOctoFireGuardPlugin(unittest.TestCase):
    """Test suite for OctoFireGuardPlugin"""

    def setUp(self):
        """Set up test fixtures before each test"""
        self.plugin = OctoFireGuardPlugin()
        
        # Mock the logger
        self.plugin._logger = Mock()
        
        # Mock the settings
        self.plugin._settings = Mock()
        self.plugin._settings.get = Mock(side_effect=self._get_setting)
        self.plugin._settings.get_boolean = Mock(side_effect=self._get_boolean_setting)
        self.plugin._settings.get_float = Mock(side_effect=self._get_float_setting)
        
        # Mock the plugin manager
        self.plugin._plugin_manager = Mock()
        
        # Mock the printer
        self.plugin._printer = Mock()
        
        # Mock the identifier
        self.plugin._identifier = "octo_fire_guard"
        
        # Mock the plugin version
        self.plugin._plugin_version = "1.0.0"
        
        # Default settings
        self.settings_dict = {
            "hotend_threshold": 250.0,
            "heatbed_threshold": 100.0,
            "termination_mode": "gcode",
            "termination_gcode": "M112\nM104 S0\nM140 S0",
            "psu_plugin_name": "psucontrol",
            "enable_monitoring": True,
            "check_interval": 1
        }
    
    def _get_setting(self, path):
        """Helper to get settings from dict"""
        key = path[0] if isinstance(path, list) else path
        return self.settings_dict.get(key)
    
    def _get_boolean_setting(self, path):
        """Helper to get boolean settings"""
        return bool(self._get_setting(path))
    
    def _get_float_setting(self, path):
        """Helper to get float settings"""
        return float(self._get_setting(path))

    # ===== Plugin Initialization Tests =====
    
    def test_plugin_initialization(self):
        """Test that plugin initializes with correct default state"""
        plugin = OctoFireGuardPlugin()
        self.assertFalse(plugin._hotend_threshold_exceeded)
        self.assertFalse(plugin._heatbed_threshold_exceeded)
        self.assertEqual(plugin._last_temperatures, {})
        self.assertIsNone(plugin._last_hotend_data_time)
        self.assertIsNone(plugin._last_heatbed_data_time)
        self.assertFalse(plugin._data_timeout_warning_sent)
        self.assertEqual(plugin._warned_missing_sensors, set())
    
    def test_get_settings_defaults(self):
        """Test that default settings are correctly defined"""
        defaults = self.plugin.get_settings_defaults()
        
        self.assertEqual(defaults["hotend_threshold"], 250)
        self.assertEqual(defaults["heatbed_threshold"], 100)
        self.assertEqual(defaults["termination_mode"], "gcode")
        self.assertIn("M112", defaults["termination_gcode"])
        self.assertEqual(defaults["psu_plugin_name"], "psucontrol")
        self.assertTrue(defaults["enable_monitoring"])
        self.assertEqual(defaults["check_interval"], 1)
        self.assertTrue(defaults["enable_data_monitoring"])
        self.assertEqual(defaults["temperature_data_timeout"], 300)
    
    def test_get_settings_version(self):
        """Test that settings version is set"""
        version = self.plugin.get_settings_version()
        self.assertEqual(version, 1)
    
    # ===== Asset Plugin Tests =====
    
    def test_get_assets(self):
        """Test that assets are properly configured"""
        assets = self.plugin.get_assets()
        
        self.assertIn("js", assets)
        self.assertIn("css", assets)
        self.assertIn("js/octo_fire_guard.js", assets["js"])
        self.assertIn("css/octo_fire_guard.css", assets["css"])
    
    # ===== Template Plugin Tests =====
    
    def test_get_template_configs(self):
        """Test that template configuration is set"""
        configs = self.plugin.get_template_configs()
        
        self.assertEqual(len(configs), 2)
        
        # Check settings template
        self.assertEqual(configs[0]["type"], "settings")
        self.assertFalse(configs[0]["custom_bindings"])
        
        # Check generic template (alert modal)
        self.assertEqual(configs[1]["type"], "generic")
        self.assertEqual(configs[1]["template"], "octo_fire_guard_alert_modal.jinja2")
        self.assertFalse(configs[1]["custom_bindings"])
    
    # ===== API Command Tests =====
    
    def test_get_api_commands(self):
        """Test that API commands are defined"""
        commands = self.plugin.get_api_commands()
        
        self.assertIn("test_alert", commands)
        self.assertEqual(commands["test_alert"], [])
    
    @patch('flask.jsonify')
    def test_on_api_command_test_alert(self, mock_jsonify):
        """Test that test_alert API command works"""
        mock_jsonify.return_value = {"success": True}
        
        result = self.plugin.on_api_command("test_alert", {})
        
        # Verify logger was called
        self.plugin._logger.info.assert_called_with("Testing alert system")
        
        # Verify plugin message was sent
        self.plugin._plugin_manager.send_plugin_message.assert_called_once()
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        
        self.assertEqual(args[0][0], "octo_fire_guard")
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "temperature_alert")
        self.assertEqual(message_data["sensor"], "test")
        self.assertEqual(message_data["current_temp"], 999)
        self.assertEqual(message_data["threshold"], 250)
        self.assertIn("test alert", message_data["message"].lower())
        
        mock_jsonify.assert_called_once_with(success=True)
    
    # ===== Temperature Callback Tests =====
    
    def test_temperature_callback_monitoring_disabled(self):
        """Test that temperature callback does nothing when monitoring is disabled"""
        self.settings_dict["enable_monitoring"] = False
        
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (80.0, 90.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should return temperatures unchanged
        self.assertEqual(result, parsed_temps)
        
        # Should not trigger any emergency
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    def test_temperature_callback_safe_temperatures(self):
        """Test that safe temperatures don't trigger alerts"""
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (80.0, 90.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should return temperatures unchanged
        self.assertEqual(result, parsed_temps)
        
        # Should not trigger any emergency
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
        self.assertFalse(self.plugin._heatbed_threshold_exceeded)
    
    def test_temperature_callback_hotend_threshold_exceeded(self):
        """Test that hotend threshold exceeded triggers emergency"""
        parsed_temps = {"tool0": (260.0, 250.0), "bed": (80.0, 90.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should return temperatures unchanged
        self.assertEqual(result, parsed_temps)
        
        # Should trigger emergency
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        self.plugin._logger.warning.assert_called()
        self.plugin._logger.error.assert_called()
        self.plugin._plugin_manager.send_plugin_message.assert_called()
        
        # Verify the alert message
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "temperature_alert")
        self.assertEqual(message_data["sensor"], "hotend")
        self.assertEqual(message_data["current_temp"], 260.0)
        self.assertEqual(message_data["threshold"], 250.0)
    
    def test_temperature_callback_heatbed_threshold_exceeded(self):
        """Test that heatbed threshold exceeded triggers emergency"""
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (110.0, 100.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should return temperatures unchanged
        self.assertEqual(result, parsed_temps)
        
        # Should trigger emergency
        self.assertTrue(self.plugin._heatbed_threshold_exceeded)
        self.plugin._logger.warning.assert_called()
        self.plugin._logger.error.assert_called()
        self.plugin._plugin_manager.send_plugin_message.assert_called()
        
        # Verify the alert message
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "temperature_alert")
        self.assertEqual(message_data["sensor"], "heatbed")
        self.assertEqual(message_data["current_temp"], 110.0)
        self.assertEqual(message_data["threshold"], 100.0)
    
    def test_temperature_callback_multiple_tools(self):
        """Test monitoring with multiple hotends"""
        parsed_temps = {
            "tool0": (200.0, 210.0),
            "tool1": (270.0, 250.0),  # This one exceeds threshold
            "bed": (80.0, 90.0)
        }
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should trigger emergency for tool1
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        self.plugin._plugin_manager.send_plugin_message.assert_called()
    
    def test_temperature_callback_threshold_reset_after_cooldown(self):
        """Test that threshold flag resets after cooldown"""
        # First trigger the threshold
        parsed_temps = {"tool0": (260.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        
        # Clear the mock to check for new calls
        self.plugin._plugin_manager.send_plugin_message.reset_mock()
        
        # Now temperature drops slightly but still above threshold
        parsed_temps = {"tool0": (255.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        # Should not trigger again
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
        
        # Temperature drops below threshold minus 10 degrees
        parsed_temps = {"tool0": (239.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
        
        # Now if it exceeds again, it should trigger
        parsed_temps = {"tool0": (260.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.plugin._plugin_manager.send_plugin_message.assert_called()
    
    def test_temperature_callback_bed_threshold_reset(self):
        """Test that bed threshold flag resets after cooldown"""
        # Trigger bed threshold
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (110.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertTrue(self.plugin._heatbed_threshold_exceeded)
        
        # Temperature drops below threshold minus 10
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (89.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._heatbed_threshold_exceeded)
    
    def test_temperature_callback_none_temperature(self):
        """Test handling of None temperature values"""
        parsed_temps = {"tool0": (None, 250.0), "bed": (None, 100.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should not crash and not trigger emergency
        self.assertEqual(result, parsed_temps)
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    def test_temperature_callback_invalid_tuple_format(self):
        """Test handling of invalid temperature tuple format"""
        parsed_temps = {"tool0": (200.0,), "bed": 80.0}  # Invalid formats
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should not crash
        self.assertEqual(result, parsed_temps)
    
    def test_temperature_callback_both_thresholds_exceeded(self):
        """Test that both hotend and bed can exceed at the same time"""
        parsed_temps = {"tool0": (260.0, 250.0), "bed": (110.0, 100.0)}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Both flags should be set
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        self.assertTrue(self.plugin._heatbed_threshold_exceeded)
        
        # Should have triggered two alerts
        self.assertEqual(self.plugin._plugin_manager.send_plugin_message.call_count, 2)
    
    # ===== Emergency Shutdown Tests =====
    
    def test_trigger_emergency_shutdown_gcode_mode(self):
        """Test emergency shutdown in gcode mode"""
        self.plugin._trigger_emergency_shutdown("hotend", 260.0, 250.0)
        
        # Verify logging
        self.plugin._logger.error.assert_called()
        
        # Verify alert sent
        self.plugin._plugin_manager.send_plugin_message.assert_called()
        
        # Verify gcode commands sent
        self.plugin._printer.commands.assert_called()
        # Should have sent M112, M104 S0, M140 S0
        self.assertEqual(self.plugin._printer.commands.call_count, 3)
    
    def test_execute_gcode_termination(self):
        """Test GCode termination execution"""
        self.plugin._execute_gcode_termination()
        
        # Verify all commands were sent
        calls = [call("M112"), call("M104 S0"), call("M140 S0")]
        self.plugin._printer.commands.assert_has_calls(calls)
        self.assertEqual(self.plugin._printer.commands.call_count, 3)
    
    def test_execute_gcode_termination_custom_commands(self):
        """Test GCode termination with custom commands"""
        self.settings_dict["termination_gcode"] = "M112\nM106 S0"
        self.plugin._execute_gcode_termination()
        
        # Verify custom commands were sent
        calls = [call("M112"), call("M106 S0")]
        self.plugin._printer.commands.assert_has_calls(calls)
        self.assertEqual(self.plugin._printer.commands.call_count, 2)
    
    def test_execute_gcode_termination_empty_lines(self):
        """Test GCode termination handles empty lines"""
        self.settings_dict["termination_gcode"] = "M112\n\nM104 S0\n\n"
        self.plugin._execute_gcode_termination()
        
        # Should only send non-empty commands
        calls = [call("M112"), call("M104 S0")]
        self.plugin._printer.commands.assert_has_calls(calls)
        self.assertEqual(self.plugin._printer.commands.call_count, 2)
    
    def test_execute_psu_termination_success(self):
        """Test PSU termination when plugin is available"""
        # Mock PSU plugin
        mock_psu_plugin = Mock()
        mock_psu_implementation = Mock()
        mock_psu_implementation.turn_psu_off = Mock()
        mock_psu_plugin.implementation = mock_psu_implementation
        
        self.plugin._plugin_manager.get_plugin_info.return_value = mock_psu_plugin
        
        self.plugin._execute_psu_termination()
        
        # Verify heaters turned off first
        calls = [call("M104 S0"), call("M140 S0")]
        self.plugin._printer.commands.assert_has_calls(calls)
        
        # Verify PSU plugin called
        mock_psu_implementation.turn_psu_off.assert_called_once()
        
        # Verify no fallback to gcode
        self.plugin._logger.warning.assert_not_called()
    
    def test_execute_psu_termination_alternative_method(self):
        """Test PSU termination with alternative method name"""
        # Mock PSU plugin with turnPSUOff method only
        mock_psu_plugin = Mock()
        mock_psu_implementation = Mock(spec=['turnPSUOff'])
        mock_psu_implementation.turnPSUOff = Mock()
        mock_psu_plugin.implementation = mock_psu_implementation
        
        self.plugin._plugin_manager.get_plugin_info.return_value = mock_psu_plugin
        
        self.plugin._execute_psu_termination()
        
        # Verify alternative method called
        mock_psu_implementation.turnPSUOff.assert_called_once()
    
    def test_execute_psu_termination_plugin_not_found(self):
        """Test PSU termination falls back when plugin not found"""
        self.plugin._plugin_manager.get_plugin_info.return_value = None
        
        self.plugin._execute_psu_termination()
        
        # Should log error and warning
        self.plugin._logger.error.assert_called()
        self.plugin._logger.warning.assert_called()
        
        # Should fall back to gcode termination
        # M104 S0, M140 S0 from PSU attempt + M112, M104 S0, M140 S0 from fallback
        self.assertTrue(self.plugin._printer.commands.call_count >= 3)
    
    def test_execute_psu_termination_no_turn_off_method(self):
        """Test PSU termination falls back when no turn off method exists"""
        # Mock PSU plugin without turn off methods
        mock_psu_plugin = Mock()
        mock_psu_implementation = Mock(spec=object)  # No methods
        mock_psu_plugin.implementation = mock_psu_implementation
        
        self.plugin._plugin_manager.get_plugin_info.return_value = mock_psu_plugin
        
        self.plugin._execute_psu_termination()
        
        # Should log warning about no method
        self.plugin._logger.warning.assert_called()
        
        # Should fall back to gcode
        self.assertTrue(self.plugin._printer.commands.call_count >= 3)
    
    def test_execute_psu_termination_exception_handling(self):
        """Test PSU termination handles exceptions gracefully"""
        # Mock PSU plugin that raises exception
        mock_psu_plugin = Mock()
        mock_psu_implementation = Mock()
        mock_psu_implementation.turn_psu_off = Mock(side_effect=Exception("Test error"))
        mock_psu_plugin.implementation = mock_psu_implementation
        
        self.plugin._plugin_manager.get_plugin_info.return_value = mock_psu_plugin
        
        self.plugin._execute_psu_termination()
        
        # Should log error and fall back
        self.plugin._logger.error.assert_called()
        self.plugin._logger.warning.assert_called()
    
    def test_trigger_emergency_shutdown_psu_mode(self):
        """Test emergency shutdown in PSU mode"""
        self.settings_dict["termination_mode"] = "psu"
        
        # Mock PSU plugin
        mock_psu_plugin = Mock()
        mock_psu_implementation = Mock()
        mock_psu_implementation.turn_psu_off = Mock()
        mock_psu_plugin.implementation = mock_psu_implementation
        self.plugin._plugin_manager.get_plugin_info.return_value = mock_psu_plugin
        
        self.plugin._trigger_emergency_shutdown("hotend", 260.0, 250.0)
        
        # Verify PSU shutdown attempted
        mock_psu_implementation.turn_psu_off.assert_called_once()
    
    def test_trigger_emergency_shutdown_unknown_mode(self):
        """Test emergency shutdown with unknown mode logs error"""
        self.settings_dict["termination_mode"] = "unknown"
        
        self.plugin._trigger_emergency_shutdown("hotend", 260.0, 250.0)
        
        # Should log error about unknown mode
        # Check that error was logged with the expected message
        self.plugin._logger.error.assert_any_call("Unknown termination mode: unknown")
    
    # ===== Update Information Tests =====
    
    def test_get_update_information(self):
        """Test that update information is properly configured"""
        update_info = self.plugin.get_update_information()
        
        self.assertIn("octo_fire_guard", update_info)
        plugin_info = update_info["octo_fire_guard"]
        
        self.assertEqual(plugin_info["displayName"], "Octo Fire Guard")
        self.assertEqual(plugin_info["type"], "github_release")
        self.assertEqual(plugin_info["user"], "rdar-lab")
        self.assertEqual(plugin_info["repo"], "octo-fire-guard")
        self.assertIn("pip", plugin_info)
    
    # ===== Edge Cases and Integration Tests =====
    
    def test_multiple_temperature_readings_same_callback(self):
        """Test handling multiple temperature readings in one callback"""
        # Simulate rapid temperature changes
        for temp in [240, 245, 252, 258, 262]:
            parsed_temps = {"tool0": (float(temp), 250.0), "bed": (80.0, 90.0)}
            self.plugin.temperature_callback(None, parsed_temps)
        
        # Should only trigger once due to flag
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        # Alert sent only once
        self.assertEqual(self.plugin._plugin_manager.send_plugin_message.call_count, 1)
    
    def test_temperature_threshold_boundary_conditions(self):
        """Test exact threshold boundary conditions"""
        # Exactly at threshold - should not trigger
        parsed_temps = {"tool0": (250.0, 250.0), "bed": (100.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
        self.assertFalse(self.plugin._heatbed_threshold_exceeded)
        
        # One degree over - should trigger
        parsed_temps = {"tool0": (251.0, 250.0), "bed": (101.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        self.assertTrue(self.plugin._heatbed_threshold_exceeded)
    
    def test_cooldown_boundary_exactly_10_degrees(self):
        """Test cooldown exactly at 10-degree threshold"""
        # Trigger alert
        parsed_temps = {"tool0": (260.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        
        # Cool down to exactly threshold - 10 (should reset)
        parsed_temps = {"tool0": (240.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
    
    def test_temperature_callback_empty_parsed_temps(self):
        """Test handling of empty temperature dictionary"""
        parsed_temps = {}
        result = self.plugin.temperature_callback(None, parsed_temps)
        
        # Should not crash
        self.assertEqual(result, parsed_temps)
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    def test_gcode_termination_with_whitespace(self):
        """Test GCode termination handles commands with whitespace"""
        self.settings_dict["termination_gcode"] = "  M112  \n  M104 S0  "
        self.plugin._execute_gcode_termination()
        
        # Commands should be stripped
        calls = [call("M112"), call("M104 S0")]
        self.plugin._printer.commands.assert_has_calls(calls)


class TestPluginHooks(unittest.TestCase):
    """Test plugin hooks and registration"""
    
    def test_plugin_load_function(self):
        """Test that __plugin_load__ function sets up hooks correctly"""
        # Call the load function to create hooks
        from octoprint_octo_fire_guard import __plugin_load__
        __plugin_load__()
        
        # Import the module to get the hooks
        from octoprint_octo_fire_guard import __plugin_hooks__
        
        self.assertIn("octoprint.plugin.softwareupdate.check_config", __plugin_hooks__)
        self.assertIn("octoprint.comm.protocol.temperatures.received", __plugin_hooks__)
    
    def test_plugin_implementation_created(self):
        """Test that __plugin_implementation__ is created"""
        from octoprint_octo_fire_guard import __plugin_load__
        __plugin_load__()
        
        from octoprint_octo_fire_guard import __plugin_implementation__
        
        self.assertIsInstance(__plugin_implementation__, OctoFireGuardPlugin)


class TestPluginIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.plugin = OctoFireGuardPlugin()
        self.plugin._logger = Mock()
        self.plugin._settings = Mock()
        self.plugin._plugin_manager = Mock()
        self.plugin._printer = Mock()
        self.plugin._identifier = "octo_fire_guard"
        self.plugin._plugin_version = "1.0.0"
        
        # Setup default settings
        settings_dict = {
            "hotend_threshold": 250.0,
            "heatbed_threshold": 100.0,
            "termination_mode": "gcode",
            "termination_gcode": "M112\nM104 S0\nM140 S0",
            "psu_plugin_name": "psucontrol",
            "enable_monitoring": True,
            "check_interval": 1
        }
        
        self.plugin._settings.get = Mock(side_effect=lambda path: settings_dict.get(path[0] if isinstance(path, list) else path))
        self.plugin._settings.get_boolean = Mock(side_effect=lambda path: bool(settings_dict.get(path[0] if isinstance(path, list) else path)))
        self.plugin._settings.get_float = Mock(side_effect=lambda path: float(settings_dict.get(path[0] if isinstance(path, list) else path)))
    
    def test_full_emergency_workflow_hotend(self):
        """Test complete emergency workflow for hotend"""
        # Start with safe temperature
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
        
        # Temperature rises above threshold
        parsed_temps = {"tool0": (265.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        # Verify emergency triggered
        self.assertTrue(self.plugin._hotend_threshold_exceeded)
        self.plugin._logger.warning.assert_called()
        self.plugin._logger.error.assert_called()
        self.plugin._plugin_manager.send_plugin_message.assert_called()
        self.plugin._printer.commands.assert_called()
        
        # Verify no repeated alerts
        self.plugin._plugin_manager.send_plugin_message.reset_mock()
        parsed_temps = {"tool0": (263.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
        
        # Temperature drops enough to reset
        parsed_temps = {"tool0": (230.0, 250.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._hotend_threshold_exceeded)
    
    def test_full_emergency_workflow_bed(self):
        """Test complete emergency workflow for bed"""
        # Temperature rises above threshold
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (115.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        # Verify emergency triggered
        self.assertTrue(self.plugin._heatbed_threshold_exceeded)
        self.plugin._plugin_manager.send_plugin_message.assert_called()
        
        # Temperature drops to reset
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (85.0, 100.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        self.assertFalse(self.plugin._heatbed_threshold_exceeded)


class TestTemperatureDataMonitoring(unittest.TestCase):
    """Test suite for temperature data timeout monitoring"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.plugin = OctoFireGuardPlugin()
        
        # Mock the logger
        self.plugin._logger = Mock()
        
        # Mock the settings
        self.plugin._settings = Mock()
        self.plugin._settings.get = Mock(side_effect=self._get_setting)
        self.plugin._settings.get_boolean = Mock(side_effect=self._get_boolean_setting)
        self.plugin._settings.get_float = Mock(side_effect=self._get_float_setting)
        self.plugin._settings.get_int = Mock(side_effect=self._get_int_setting)
        
        # Mock the plugin manager
        self.plugin._plugin_manager = Mock()
        
        # Mock the printer
        self.plugin._printer = Mock()
        self.plugin._printer.is_operational = Mock(return_value=True)
        self.plugin._printer.is_printing = Mock(return_value=False)
        
        # Mock the identifier
        self.plugin._identifier = "octo_fire_guard"
        
        # Default settings
        self.settings_dict = {
            "hotend_threshold": 250.0,
            "heatbed_threshold": 100.0,
            "termination_mode": "gcode",
            "termination_gcode": "M112\nM104 S0\nM140 S0",
            "psu_plugin_name": "psucontrol",
            "enable_monitoring": True,
            "check_interval": 1,
            "enable_data_monitoring": True,
            "temperature_data_timeout": 300
        }
    
    def _get_setting(self, path):
        """Helper to get settings from dict"""
        key = path[0] if isinstance(path, list) else path
        return self.settings_dict.get(key)
    
    def _get_boolean_setting(self, path):
        """Helper to get boolean settings"""
        return bool(self._get_setting(path))
    
    def _get_float_setting(self, path):
        """Helper to get float settings"""
        return float(self._get_setting(path))
    
    def _get_int_setting(self, path):
        """Helper to get int settings"""
        val = self._get_setting(path)
        return int(val) if val is not None else 0
    
    def test_initialization_new_fields(self):
        """Test that new monitoring fields are initialized"""
        plugin = OctoFireGuardPlugin()
        self.assertIsNone(plugin._last_hotend_data_time)
        self.assertIsNone(plugin._last_heatbed_data_time)
        self.assertFalse(plugin._data_timeout_warning_sent)
        self.assertIsNone(plugin._monitoring_timer)
        self.assertEqual(plugin._warned_missing_sensors, set())
    
    def test_get_settings_defaults_includes_monitoring(self):
        """Test that new settings are in defaults"""
        defaults = self.plugin.get_settings_defaults()
        self.assertIn("enable_data_monitoring", defaults)
        self.assertIn("temperature_data_timeout", defaults)
        self.assertTrue(defaults["enable_data_monitoring"])
        self.assertEqual(defaults["temperature_data_timeout"], 300)
    
    def test_temperature_callback_updates_hotend_time(self):
        """Test that temperature callback updates hotend data time"""
        import time
        before = time.time()
        
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        after = time.time()
        
        self.assertIsNotNone(self.plugin._last_hotend_data_time)
        self.assertGreaterEqual(self.plugin._last_hotend_data_time, before)
        self.assertLessEqual(self.plugin._last_hotend_data_time, after)
    
    def test_temperature_callback_updates_heatbed_time(self):
        """Test that temperature callback updates heatbed data time"""
        import time
        before = time.time()
        
        parsed_temps = {"tool0": (200.0, 210.0), "bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        after = time.time()
        
        self.assertIsNotNone(self.plugin._last_heatbed_data_time)
        self.assertGreaterEqual(self.plugin._last_heatbed_data_time, before)
        self.assertLessEqual(self.plugin._last_heatbed_data_time, after)
    
    def test_temperature_callback_does_not_update_on_none(self):
        """Test that None temperature doesn't update timestamps"""
        parsed_temps = {"tool0": (None, 210.0), "bed": (None, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        # Should remain None
        self.assertIsNone(self.plugin._last_hotend_data_time)
        self.assertIsNone(self.plugin._last_heatbed_data_time)
    
    def test_check_timeout_when_printer_not_operational(self):
        """Test that timeout check does nothing when printer not operational"""
        self.plugin._printer.is_operational.return_value = False
        self.plugin._last_hotend_data_time = 100.0
        self.plugin._last_heatbed_data_time = 100.0
        
        self.plugin._check_temperature_data_timeout()
        
        # Should reset times when not operational
        self.assertIsNone(self.plugin._last_hotend_data_time)
        self.assertIsNone(self.plugin._last_heatbed_data_time)
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    def test_check_timeout_when_monitoring_disabled(self):
        """Test that timeout check does nothing when monitoring disabled"""
        self.settings_dict["enable_data_monitoring"] = False
        
        self.plugin._check_temperature_data_timeout()
        
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    @patch('time.time')
    def test_check_timeout_hotend_timeout_detected(self, mock_time):
        """Test that hotend timeout is detected"""
        # Set last data time to 400 seconds ago
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 600.0  # 400 seconds ago
        self.plugin._last_heatbed_data_time = 950.0  # Recent
        
        self.plugin._check_temperature_data_timeout()
        
        # Should send warning
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        self.plugin._plugin_manager.send_plugin_message.assert_called_once()
        
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "data_timeout_warning")
        self.assertIn("hotend", message_data["sensors"])
        self.assertNotIn("heatbed", message_data["sensors"])
    
    @patch('time.time')
    def test_check_timeout_heatbed_timeout_detected(self, mock_time):
        """Test that heatbed timeout is detected"""
        # Set last data time to 400 seconds ago
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 950.0  # Recent
        self.plugin._last_heatbed_data_time = 600.0  # 400 seconds ago
        
        self.plugin._check_temperature_data_timeout()
        
        # Should send warning
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        self.plugin._plugin_manager.send_plugin_message.assert_called_once()
        
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "data_timeout_warning")
        self.assertIn("heatbed", message_data["sensors"])
        self.assertNotIn("hotend", message_data["sensors"])
    
    @patch('time.time')
    def test_check_timeout_both_sensors_timeout(self, mock_time):
        """Test that both sensor timeouts are detected"""
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 600.0  # 400 seconds ago
        self.plugin._last_heatbed_data_time = 600.0  # 400 seconds ago
        
        self.plugin._check_temperature_data_timeout()
        
        # Should send warning with both sensors
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertIn("hotend", message_data["sensors"])
        self.assertIn("heatbed", message_data["sensors"])
    
    @patch('time.time')
    def test_check_timeout_no_warning_when_within_timeout(self, mock_time):
        """Test that no warning when temperature data is recent"""
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 900.0  # 100 seconds ago (< 300)
        self.plugin._last_heatbed_data_time = 900.0  # 100 seconds ago (< 300)
        
        self.plugin._check_temperature_data_timeout()
        
        # Should not send warning
        self.assertFalse(self.plugin._data_timeout_warning_sent)
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    @patch('time.time')
    def test_check_timeout_warning_sent_only_once(self, mock_time):
        """Test that warning is only sent once"""
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 600.0
        
        # First check - should send warning
        self.plugin._check_temperature_data_timeout()
        self.assertEqual(self.plugin._plugin_manager.send_plugin_message.call_count, 1)
        
        # Second check - should not send again
        self.plugin._plugin_manager.send_plugin_message.reset_mock()
        self.plugin._check_temperature_data_timeout()
        self.plugin._plugin_manager.send_plugin_message.assert_not_called()
    
    @patch('time.time')
    def test_check_timeout_warning_clears_when_data_resumes(self, mock_time):
        """Test that warning clears when data resumes"""
        # First, trigger a timeout
        mock_time.return_value = 1000.0
        self.plugin._last_hotend_data_time = 600.0
        self.plugin._check_temperature_data_timeout()
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        
        # Now data resumes
        mock_time.return_value = 1050.0
        self.plugin._last_hotend_data_time = 1050.0  # Updated to current time
        self.plugin._check_temperature_data_timeout()
        
        # Warning state should clear
        self.assertFalse(self.plugin._data_timeout_warning_sent)
    
    def test_temperature_callback_clears_warning_on_data_resume(self):
        """Test that temperature callback clears warning when data resumes"""
        # Set warning state for both sensors
        self.plugin._data_timeout_warning_sent = True
        self.plugin._warned_missing_sensors = {"hotend", "heatbed"}
        
        # Receive temperature data for hotend only
        parsed_temps = {"tool0": (200.0, 210.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        # Hotend should be removed from warned sensors, but warning state should remain
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        self.assertEqual(self.plugin._warned_missing_sensors, {"heatbed"})
        self.plugin._logger.info.assert_any_call("Hotend temperature data resumed")
        
        # Reset for bed test
        self.plugin._logger.info.reset_mock()
        
        # Receive temperature data for bed
        parsed_temps = {"bed": (80.0, 90.0)}
        self.plugin.temperature_callback(None, parsed_temps)
        
        # All sensors cleared, warning state should be cleared now
        self.assertFalse(self.plugin._data_timeout_warning_sent)
        self.assertEqual(self.plugin._warned_missing_sensors, set())
        self.plugin._logger.info.assert_any_call("Heatbed temperature data resumed")
    
    def test_send_data_timeout_warning_message_format(self):
        """Test the format of timeout warning message"""
        missing_sensors = ["hotend", "heatbed"]
        timeout = 300
        
        self.plugin._send_data_timeout_warning(missing_sensors, timeout)
        
        # Check logger was called
        self.plugin._logger.warning.assert_called_once()
        
        # Check plugin message
        self.plugin._plugin_manager.send_plugin_message.assert_called_once()
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        
        self.assertEqual(args[0][0], "octo_fire_guard")
        message_data = args[0][1]
        self.assertEqual(message_data["type"], "data_timeout_warning")
        self.assertEqual(message_data["sensors"], ["hotend", "heatbed"])
        self.assertEqual(message_data["timeout"], 300)
        self.assertIn("5 minutes", message_data["message"])
        self.assertIn("hotend and heatbed", message_data["message"])
    
    @patch('time.time')
    def test_check_timeout_never_received_data_after_startup(self, mock_time):
        """Test that timeout is detected when no hotend data received after startup timeout"""
        # Set startup time far in the past
        mock_time.return_value = 1000.0
        self.plugin._startup_time = 600.0  # 400 seconds ago
        # Never received any data
        self.plugin._last_hotend_data_time = None
        self.plugin._last_heatbed_data_time = None
        
        self.plugin._check_temperature_data_timeout()
        
        # Should warn about hotend only (heatbed warning only happens if we've seen it before)
        self.assertTrue(self.plugin._data_timeout_warning_sent)
        self.plugin._plugin_manager.send_plugin_message.assert_called_once()
        
        args = self.plugin._plugin_manager.send_plugin_message.call_args
        message_data = args[0][1]
        self.assertIn("hotend", message_data["sensors"])
        # Heatbed should NOT be warned about since we never received data from it
        # (some printers don't have heatbeds)
        self.assertNotIn("heatbed", message_data["sensors"])


if __name__ == '__main__':
    unittest.main()
