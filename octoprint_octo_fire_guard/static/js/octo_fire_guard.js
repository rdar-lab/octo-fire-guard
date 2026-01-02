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

        // Load settings from the plugin settings
        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings.plugins.octo_fire_guard;
            if (self.settings) {
                self.hotend_threshold(self.settings.hotend_threshold());
                self.heatbed_threshold(self.settings.heatbed_threshold());
                self.termination_mode(self.settings.termination_mode());
                self.termination_gcode(self.settings.termination_gcode());
                self.psu_plugin_name(self.settings.psu_plugin_name());
                self.enable_monitoring(self.settings.enable_monitoring());
            }
        };

        // Manual binding for compatibility with UI Customizer and other DOM-modifying plugins
        self.onAfterBinding = function() {
            // Bind the alert modal manually if it hasn't been bound yet
            var alertModal = document.getElementById("octo_fire_guard_alert_modal");
            if (alertModal) {
                var existingBinding = ko.dataFor(alertModal);
                // Only bind if not already bound to this viewModel instance
                if (!existingBinding || existingBinding !== self) {
                    try {
                        ko.applyBindings(self, alertModal);
                    } catch (e) {
                        // If binding fails (e.g., already bound), log but don't break functionality
                        console.error("Octo Fire Guard: Could not bind alert modal", e);
                    }
                }
            }
        };

        // Handle messages from the backend
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "octo_fire_guard") {
                return;
            }

            if (data.type === "temperature_alert") {
                self.showAlert(data);
            }
        };

        // Show alert popup
        self.showAlert = function(data) {
            self.alertMessage(data.message);
            self.alertSensor(data.sensor);
            self.alertCurrentTemp(data.current_temp);
            self.alertThreshold(data.threshold);
            self.isAlertVisible(true);

            // Play alert sound if available
            if (typeof Audio !== "undefined") {
                try {
                    var audio = new Audio("data:audio/wav;base64,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");
                    audio.play();
                } catch(e) {
                    console.error("Could not play alert sound:", e);
                }
            }
        };

        // Close alert
        self.closeAlert = function() {
            self.isAlertVisible(false);
        };

        // Test alert functionality
        self.testAlert = function() {
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
        };
    }

    // Register the view model with empty elements array to avoid conflicts with UI Customizer
    // OctoPrint's automatic binding will handle #settings_plugin_octo_fire_guard (settings panel)
    // We manually bind #octo_fire_guard_alert_modal in onAfterBinding for better compatibility
    OCTOPRINT_VIEWMODELS.push({
        construct: OctoFireGuardViewModel,
        dependencies: ["settingsViewModel"],
        elements: []
    });
});
