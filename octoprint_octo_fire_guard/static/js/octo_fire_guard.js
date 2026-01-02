/*
 * View model for Octo Fire Guard
 * Author: OctoPrint Fire Guard Team
 * License: AGPLv3
 */

$(function() {
    function OctoFireGuardViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        // Settings observables
        self.hotend_threshold = ko.observable();
        self.heatbed_threshold = ko.observable();
        self.termination_mode = ko.observable();
        self.termination_gcode = ko.observable();
        self.psu_plugin_name = ko.observable();
        self.enable_monitoring = ko.observable();

        // UI state
        self.isAlertVisible = ko.observable(false);
        self.alertMessage = ko.observable("");
        self.alertSensor = ko.observable("");
        self.alertCurrentTemp = ko.observable(0);
        self.alertThreshold = ko.observable(0);
        self.alertAudioInterval = null;  // For continuous beeping
        
        // Alert sound data (base64-encoded WAV)
        self.alertSoundData = "data:audio/wav;base64,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";

        // Load settings from the plugin settings
        self.onBeforeBinding = function() {
            try {
                self.settings = self.settingsViewModel.settings.plugins.octo_fire_guard;
                if (self.settings) {
                    self.hotend_threshold(self.settings.hotend_threshold());
                    self.heatbed_threshold(self.settings.heatbed_threshold());
                    self.termination_mode(self.settings.termination_mode());
                    self.termination_gcode(self.settings.termination_gcode());
                    self.psu_plugin_name(self.settings.psu_plugin_name());
                    self.enable_monitoring(self.settings.enable_monitoring());
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error loading settings", e);
            }
        };

        // Manual setup in onAfterBinding for UI elements that need special handling
        self.onAfterBinding = function() {
            try {
                // Attach event listener to test alert button
                var testButton = document.getElementById("octo-fire-guard-test-alert-btn");
                if (testButton) {
                    testButton.addEventListener("click", function(e) {
                        e.preventDefault();
                        try {
                            self.testAlert();
                        } catch (err) {
                            console.error("Octo Fire Guard: Error calling testAlert", err);
                        }
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error in onAfterBinding", e);
            }
        };

        // Handle messages from the backend
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "octo_fire_guard") {
                return;
            }

            if (data.type === "temperature_alert") {
                self.showAlert(data);
            } else if (data.type === "data_timeout_warning") {
                self.showDataTimeoutWarning(data);
            }
        };

        // Show alert popup
        self.showAlert = function(data) {
            try {
                self.alertMessage(data.message);
                self.alertSensor(data.sensor);
                self.alertCurrentTemp(data.current_temp);
                self.alertThreshold(data.threshold);
                self.isAlertVisible(true);

                // Show the Bootstrap modal
                var modal = $("#octo_fire_guard_alert_modal");
                if (modal.length) {
                    modal.modal({
                        backdrop: "static",  // Prevent closing by clicking outside
                        keyboard: false      // Prevent closing with ESC key
                    });
                    modal.modal("show");
                }

                // Play continuous alert sound
                self.startAlertSound();

                // Show OctoPrint notification
                if (typeof PNotify !== "undefined") {
                    new PNotify({
                        title: "Temperature Alert!",
                        text: data.message + " - " + data.sensor + ": " + data.current_temp + "°C (Threshold: " + data.threshold + "°C)",
                        type: "error",
                        hide: false,  // Don't auto-hide
                        icon: "fa fa-fire"
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error showing alert", e);
            }
        };

        // Start continuous alert sound
        self.startAlertSound = function() {
            // Stop any existing alert sound
            self.stopAlertSound();

            if (typeof Audio !== "undefined") {
                try {
                    var audio = new Audio(self.alertSoundData);
                    
                    // Play sound immediately
                    audio.play();
                    
                    // Set up interval for continuous beeping (every 2 seconds)
                    self.alertAudioInterval = setInterval(function() {
                        try {
                            var beep = new Audio(self.alertSoundData);
                            beep.play();
                        } catch(e) {
                            console.error("Could not play continuous alert sound:", e);
                        }
                    }, 2000);
                } catch(e) {
                    console.error("Could not start alert sound:", e);
                }
            }
        };

        // Stop continuous alert sound
        self.stopAlertSound = function() {
            if (self.alertAudioInterval) {
                clearInterval(self.alertAudioInterval);
                self.alertAudioInterval = null;
            }
        };

        // Close alert
        self.closeAlert = function() {
            try {
                self.isAlertVisible(false);
                
                // Stop continuous beeping
                self.stopAlertSound();
                
                // Hide the Bootstrap modal
                var modal = $("#octo_fire_guard_alert_modal");
                if (modal.length) {
                    modal.modal("hide");
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error closing alert", e);
            }
        };

        // Show data timeout warning notification
        self.showDataTimeoutWarning = function(data) {
            try {
                var sensorsStr = data.sensors.join(" and ");
                var timeoutMinutes = Math.floor(data.timeout / 60);
                
                console.warn("Octo Fire Guard: Temperature data timeout - " + data.message);
                
                // Show OctoPrint notification
                if (typeof PNotify !== "undefined") {
                    new PNotify({
                        title: "Octo Fire Guard: Self-Test Warning",
                        text: "No temperature data received from " + sensorsStr + " for " + timeoutMinutes + " minutes. " +
                              "The plugin may not be monitoring correctly. Please check your printer connection.",
                        type: "warning",
                        hide: false,  // Don't auto-hide
                        icon: "fa fa-exclamation-triangle"
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error showing data timeout warning", e);
            }
        };

        // Test alert functionality
        self.testAlert = function() {
            try {
                // Defensive check to ensure OctoPrint API is available
                if (typeof OctoPrint === "undefined" || !OctoPrint.simpleApiCommand) {
                    console.error("Octo Fire Guard: OctoPrint API not available");
                    return;
                }
                
                OctoPrint.simpleApiCommand("octo_fire_guard", "test_alert")
                    .done(function(response) {
                        console.log("Test alert sent");
                    })
                    .fail(function(xhr, status, error) {
                        console.error("Failed to send test alert:", status, error);
                    });
            } catch (e) {
                console.error("Octo Fire Guard: Error in testAlert", e);
            }
        };
    }

    // Register the view model with the alert modal element for binding
    // The modal is in a separate generic template to avoid binding conflicts with SettingsViewModel
    // The test alert button uses a direct event listener to avoid Knockout binding context issues
    OCTOPRINT_VIEWMODELS.push({
        construct: OctoFireGuardViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#octo_fire_guard_alert_modal"]
    });
});
