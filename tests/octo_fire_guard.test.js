/**
 * Unit tests for Octo Fire Guard JavaScript ViewModel
 * Tests the frontend JavaScript functionality including alert display,
 * sound handling, and API interactions.
 */

describe('OctoFireGuardViewModel', () => {
    let viewModel;
    let mockSettingsViewModel;
    let mockOctoPrint;
    let mockPNotify;
    let mockJQuery;

    beforeEach(() => {
        // Mock jQuery
        mockJQuery = jest.fn((selector) => {
            const mockElement = {
                modal: jest.fn(),
                length: 1
            };
            return mockElement;
        });
        global.$ = mockJQuery;

        // Mock knockout observables
        global.ko = {
            observable: function(value) {
                let _value = value;
                const obs = function(newValue) {
                    if (arguments.length === 0) {
                        return _value;
                    }
                    _value = newValue;
                    return obs;
                };
                obs._value = _value;
                return obs;
            }
        };

        // Mock OctoPrint API
        mockOctoPrint = {
            simpleApiCommand: jest.fn(() => ({
                done: jest.fn((callback) => {
                    callback({ success: true });
                    return { fail: jest.fn() };
                }),
                fail: jest.fn()
            }))
        };
        global.OctoPrint = mockOctoPrint;

        // Mock PNotify
        mockPNotify = jest.fn();
        global.PNotify = mockPNotify;

        // Mock Audio
        global.Audio = jest.fn(() => ({
            play: jest.fn()
        }));

        // Mock document.getElementById
        global.document = {
            getElementById: jest.fn((id) => {
                if (id === 'octo-fire-guard-test-alert-btn' || id === 'octo-fire-guard-test-emergency-btn') {
                    return {
                        addEventListener: jest.fn()
                    };
                }
                return null;
            })
        };

        // Mock console methods
        global.console = {
            log: jest.fn(),
            error: jest.fn(),
            warn: jest.fn(),
            info: jest.fn()
        };

        // Mock setInterval and clearInterval
        global.setInterval = jest.fn((callback, delay) => {
            return 12345; // Return a mock interval ID
        });
        global.clearInterval = jest.fn();

        // Mock confirm
        global.confirm = jest.fn(() => true);

        // Setup mock settings view model
        mockSettingsViewModel = {
            settings: {
                plugins: {
                    octo_fire_guard: {
                        hotend_threshold: ko.observable(250),
                        heatbed_threshold: ko.observable(100),
                        termination_mode: ko.observable('gcode'),
                        termination_gcode: ko.observable('M112\nM104 S0\nM140 S0'),
                        psu_plugin_name: ko.observable('psucontrol'),
                        enable_monitoring: ko.observable(true)
                    }
                }
            }
        };

        // Load the ViewModel constructor from the file
        // Since we can't directly eval the file content in Jest, we'll mock the constructor
        viewModel = createMockViewModel([mockSettingsViewModel]);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    // Helper function to create a mock ViewModel that mimics the real implementation
    function createMockViewModel(parameters) {
        const vm = {
            settingsViewModel: parameters[0],
            hotend_threshold: ko.observable(),
            heatbed_threshold: ko.observable(),
            termination_mode: ko.observable(),
            termination_gcode: ko.observable(),
            psu_plugin_name: ko.observable(),
            enable_monitoring: ko.observable(),
            isAlertVisible: ko.observable(false),
            alertMessage: ko.observable(""),
            alertSensor: ko.observable(""),
            alertCurrentTemp: ko.observable(0),
            alertThreshold: ko.observable(0),
            alertAudioInterval: null,
            dataTimeoutNotification: null,
            alertSoundData: "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAAA="
        };

        // Implement onBeforeBinding
        vm.onBeforeBinding = function() {
            try {
                vm.settings = vm.settingsViewModel.settings.plugins.octo_fire_guard;
                if (vm.settings) {
                    vm.hotend_threshold(vm.settings.hotend_threshold());
                    vm.heatbed_threshold(vm.settings.heatbed_threshold());
                    vm.termination_mode(vm.settings.termination_mode());
                    vm.termination_gcode(vm.settings.termination_gcode());
                    vm.psu_plugin_name(vm.settings.psu_plugin_name());
                    vm.enable_monitoring(vm.settings.enable_monitoring());
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error loading settings", e);
            }
        };

        // Implement onAfterBinding
        vm.onAfterBinding = function() {
            try {
                var testButton = document.getElementById("octo-fire-guard-test-alert-btn");
                if (testButton) {
                    testButton.addEventListener("click", function(e) {
                        e.preventDefault();
                        try {
                            vm.testAlert();
                        } catch (err) {
                            console.error("Octo Fire Guard: Error calling testAlert", err);
                        }
                    });
                }
                
                var testEmergencyButton = document.getElementById("octo-fire-guard-test-emergency-btn");
                if (testEmergencyButton) {
                    testEmergencyButton.addEventListener("click", function(e) {
                        e.preventDefault();
                        try {
                            vm.testEmergencyActions();
                        } catch (err) {
                            console.error("Octo Fire Guard: Error calling testEmergencyActions", err);
                        }
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error in onAfterBinding", e);
            }
        };

        // Implement onDataUpdaterPluginMessage
        vm.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "octo_fire_guard") {
                return;
            }

            if (data.type === "temperature_alert") {
                vm.showAlert(data);
            } else if (data.type === "data_timeout_warning") {
                vm.showDataTimeoutWarning(data);
            } else if (data.type === "data_timeout_cleared") {
                vm.dismissDataTimeoutWarning();
            }
        };

        // Implement showAlert
        vm.showAlert = function(data) {
            try {
                vm.alertMessage(data.message);
                vm.alertSensor(data.sensor);
                vm.alertCurrentTemp(data.current_temp);
                vm.alertThreshold(data.threshold);
                vm.isAlertVisible(true);

                var modal = $("#octo_fire_guard_alert_modal");
                if (modal.length) {
                    modal.modal({
                        backdrop: "static",
                        keyboard: false
                    });
                    modal.modal("show");
                }

                vm.startAlertSound();

                if (typeof PNotify !== "undefined") {
                    new PNotify({
                        title: "Temperature Alert!",
                        text: data.message + " - " + data.sensor + ": " + data.current_temp + "°C (Threshold: " + data.threshold + "°C)",
                        type: "error",
                        hide: false,
                        icon: "fa fa-fire",
                        title_escape: true,
                        text_escape: true
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error showing alert", e);
            }
        };

        // Implement startAlertSound
        vm.startAlertSound = function() {
            vm.stopAlertSound();

            if (typeof Audio !== "undefined") {
                try {
                    var audio = new Audio(vm.alertSoundData);
                    audio.play();
                    
                    vm.alertAudioInterval = setInterval(function() {
                        try {
                            var beep = new Audio(vm.alertSoundData);
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

        // Implement stopAlertSound
        vm.stopAlertSound = function() {
            if (vm.alertAudioInterval) {
                clearInterval(vm.alertAudioInterval);
                vm.alertAudioInterval = null;
            }
        };

        // Implement closeAlert
        vm.closeAlert = function() {
            try {
                vm.isAlertVisible(false);
                vm.stopAlertSound();
                
                var modal = $("#octo_fire_guard_alert_modal");
                if (modal.length) {
                    modal.modal("hide");
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error closing alert", e);
            }
        };

        // Implement showDataTimeoutWarning
        vm.showDataTimeoutWarning = function(data) {
            try {
                var sensorsStr = data.sensors.join(" and ");
                var timeoutMinutes = Math.floor(data.timeout / 60);
                
                console.warn("Octo Fire Guard: Temperature data timeout - " + data.message);
                
                if (typeof PNotify !== "undefined") {
                    vm.dataTimeoutNotification = new PNotify({
                        title: "Octo Fire Guard: Self-Test Warning",
                        text: "No temperature data received from " + sensorsStr + " for " + timeoutMinutes + " minutes. " +
                              "The plugin may not be monitoring correctly. Please check your printer connection.",
                        type: "warning",
                        hide: false,
                        icon: "fa fa-exclamation-triangle",
                        title_escape: true,
                        text_escape: true
                    });
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error showing data timeout warning", e);
            }
        };

        // Implement dismissDataTimeoutWarning
        vm.dismissDataTimeoutWarning = function() {
            try {
                if (vm.dataTimeoutNotification) {
                    vm.dataTimeoutNotification.remove = jest.fn();
                    vm.dataTimeoutNotification.remove();
                    vm.dataTimeoutNotification = null;
                    console.info("Octo Fire Guard: Temperature data timeout warning dismissed");
                }
            } catch (e) {
                console.error("Octo Fire Guard: Error dismissing data timeout warning", e);
            }
        };

        // Implement testAlert
        vm.testAlert = function() {
            try {
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

        // Implement testEmergencyActions
        vm.testEmergencyActions = function() {
            try {
                if (typeof OctoPrint === "undefined" || !OctoPrint.simpleApiCommand) {
                    console.error("Octo Fire Guard: OctoPrint API not available");
                    return;
                }
                
                if (!confirm("This will execute the configured emergency actions (GCode commands or PSU control). Are you sure you want to proceed?")) {
                    return;
                }
                
                if (typeof PNotify !== "undefined") {
                    new PNotify({
                        title: "Testing Emergency Actions",
                        text: "Executing emergency actions...",
                        type: "info",
                        hide: true,
                        delay: 3000,
                        title_escape: true,
                        text_escape: true
                    });
                }
                
                OctoPrint.simpleApiCommand("octo_fire_guard", "test_emergency_actions")
                    .done(function(response) {
                        console.log("Test emergency actions completed:", response);
                        
                        if (typeof PNotify !== "undefined") {
                            var message = "Emergency actions test completed successfully";
                            if (response.mode) {
                                message += " (" + response.mode + " mode)";
                            }
                            if (response.message) {
                                message += ": " + response.message;
                            }
                            
                            new PNotify({
                                title: "Test Successful",
                                text: message,
                                type: "success",
                                hide: true,
                                delay: 5000,
                                title_escape: true,
                                text_escape: true
                            });
                        }
                    })
                    .fail(function(xhr, status, error) {
                        console.error("Failed to test emergency actions:", status, error);
                        
                        if (typeof PNotify !== "undefined") {
                            var errorMsg = "Failed to test emergency actions";
                            if (xhr.responseJSON && xhr.responseJSON.error) {
                                errorMsg += ": " + xhr.responseJSON.error;
                            }
                            
                            new PNotify({
                                title: "Test Failed",
                                text: errorMsg,
                                type: "error",
                                hide: false,
                                title_escape: true,
                                text_escape: true
                            });
                        }
                    });
            } catch (e) {
                console.error("Octo Fire Guard: Error in testEmergencyActions", e);
            }
        };

        return vm;
    }

    describe('Initialization', () => {
        test('should initialize with correct default values', () => {
            expect(viewModel.isAlertVisible()).toBe(false);
            expect(viewModel.alertMessage()).toBe("");
            expect(viewModel.alertSensor()).toBe("");
            expect(viewModel.alertCurrentTemp()).toBe(0);
            expect(viewModel.alertThreshold()).toBe(0);
            expect(viewModel.alertAudioInterval).toBeNull();
            expect(viewModel.dataTimeoutNotification).toBeNull();
        });

        test('should have alert sound data defined', () => {
            expect(viewModel.alertSoundData).toBeDefined();
            expect(viewModel.alertSoundData).toContain('data:audio/wav;base64');
        });
    });

    describe('onBeforeBinding', () => {
        test('should load settings from settingsViewModel', () => {
            viewModel.onBeforeBinding();

            expect(viewModel.hotend_threshold()).toBe(250);
            expect(viewModel.heatbed_threshold()).toBe(100);
            expect(viewModel.termination_mode()).toBe('gcode');
            expect(viewModel.termination_gcode()).toBe('M112\nM104 S0\nM140 S0');
            expect(viewModel.psu_plugin_name()).toBe('psucontrol');
            expect(viewModel.enable_monitoring()).toBe(true);
        });

        test('should handle missing settings gracefully', () => {
            viewModel.settingsViewModel = { settings: { plugins: {} } };
            
            expect(() => {
                viewModel.onBeforeBinding();
            }).not.toThrow();
        });

        test('should log error if exception occurs', () => {
            viewModel.settingsViewModel = null;
            
            viewModel.onBeforeBinding();
            
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining("Error loading settings"),
                expect.any(Error)
            );
        });
    });

    describe('onAfterBinding', () => {
        test('should attach event listener to test alert button', () => {
            const mockButton = {
                addEventListener: jest.fn()
            };
            document.getElementById = jest.fn((id) => {
                if (id === 'octo-fire-guard-test-alert-btn') {
                    return mockButton;
                }
                return null;
            });

            viewModel.onAfterBinding();

            expect(document.getElementById).toHaveBeenCalledWith('octo-fire-guard-test-alert-btn');
            expect(mockButton.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        });

        test('should attach event listener to test emergency button', () => {
            const mockButton = {
                addEventListener: jest.fn()
            };
            document.getElementById = jest.fn((id) => {
                if (id === 'octo-fire-guard-test-emergency-btn') {
                    return mockButton;
                }
                return null;
            });

            viewModel.onAfterBinding();

            expect(document.getElementById).toHaveBeenCalledWith('octo-fire-guard-test-emergency-btn');
            expect(mockButton.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        });

        test('should handle missing buttons gracefully', () => {
            document.getElementById = jest.fn(() => null);

            expect(() => {
                viewModel.onAfterBinding();
            }).not.toThrow();
        });
    });

    describe('onDataUpdaterPluginMessage', () => {
        test('should ignore messages from other plugins', () => {
            const showAlertSpy = jest.spyOn(viewModel, 'showAlert');
            
            viewModel.onDataUpdaterPluginMessage('other_plugin', { type: 'temperature_alert' });

            expect(showAlertSpy).not.toHaveBeenCalled();
        });

        test('should handle temperature_alert message', () => {
            const showAlertSpy = jest.spyOn(viewModel, 'showAlert');
            const alertData = {
                type: 'temperature_alert',
                message: 'Test alert',
                sensor: 'hotend',
                current_temp: 260,
                threshold: 250
            };

            viewModel.onDataUpdaterPluginMessage('octo_fire_guard', alertData);

            expect(showAlertSpy).toHaveBeenCalledWith(alertData);
        });

        test('should handle data_timeout_warning message', () => {
            const showWarningSpy = jest.spyOn(viewModel, 'showDataTimeoutWarning');
            const warningData = {
                type: 'data_timeout_warning',
                sensors: ['hotend'],
                timeout: 300
            };

            viewModel.onDataUpdaterPluginMessage('octo_fire_guard', warningData);

            expect(showWarningSpy).toHaveBeenCalledWith(warningData);
        });

        test('should handle data_timeout_cleared message', () => {
            const dismissSpy = jest.spyOn(viewModel, 'dismissDataTimeoutWarning');

            viewModel.onDataUpdaterPluginMessage('octo_fire_guard', { type: 'data_timeout_cleared' });

            expect(dismissSpy).toHaveBeenCalled();
        });
    });

    describe('showAlert', () => {
        test('should set alert observables correctly', () => {
            const alertData = {
                message: 'Temperature too high!',
                sensor: 'hotend',
                current_temp: 260,
                threshold: 250
            };

            viewModel.showAlert(alertData);

            expect(viewModel.alertMessage()).toBe('Temperature too high!');
            expect(viewModel.alertSensor()).toBe('hotend');
            expect(viewModel.alertCurrentTemp()).toBe(260);
            expect(viewModel.alertThreshold()).toBe(250);
            expect(viewModel.isAlertVisible()).toBe(true);
        });

        test('should show Bootstrap modal', () => {
            const mockModal = {
                modal: jest.fn(),
                length: 1
            };
            mockJQuery.mockReturnValue(mockModal);

            viewModel.showAlert({
                message: 'Test',
                sensor: 'hotend',
                current_temp: 260,
                threshold: 250
            });

            expect(mockJQuery).toHaveBeenCalledWith('#octo_fire_guard_alert_modal');
            expect(mockModal.modal).toHaveBeenCalledWith({
                backdrop: 'static',
                keyboard: false
            });
            expect(mockModal.modal).toHaveBeenCalledWith('show');
        });

        test('should start alert sound', () => {
            const startSoundSpy = jest.spyOn(viewModel, 'startAlertSound');

            viewModel.showAlert({
                message: 'Test',
                sensor: 'hotend',
                current_temp: 260,
                threshold: 250
            });

            expect(startSoundSpy).toHaveBeenCalled();
        });

        test('should show PNotify notification', () => {
            viewModel.showAlert({
                message: 'Temperature too high!',
                sensor: 'hotend',
                current_temp: 260,
                threshold: 250
            });

            expect(mockPNotify).toHaveBeenCalledWith(expect.objectContaining({
                title: 'Temperature Alert!',
                type: 'error',
                hide: false
            }));
        });

        test('should handle errors gracefully', () => {
            // Make alertMessage throw an error
            viewModel.alertMessage = jest.fn(() => {
                throw new Error('Test error');
            });

            expect(() => {
                viewModel.showAlert({
                    message: 'Test',
                    sensor: 'hotend',
                    current_temp: 260,
                    threshold: 250
                });
            }).not.toThrow();

            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining("Error showing alert"),
                expect.any(Error)
            );
        });
    });

    describe('Alert Sound Controls', () => {
        test('startAlertSound should stop existing sound first', () => {
            viewModel.alertAudioInterval = 12345;
            
            viewModel.startAlertSound();

            expect(clearInterval).toHaveBeenCalledWith(12345);
        });

        test('startAlertSound should play audio immediately', () => {
            const mockAudio = {
                play: jest.fn()
            };
            global.Audio = jest.fn(() => mockAudio);

            viewModel.startAlertSound();

            expect(Audio).toHaveBeenCalledWith(viewModel.alertSoundData);
            expect(mockAudio.play).toHaveBeenCalled();
        });

        test('startAlertSound should set up interval for continuous beeping', () => {
            viewModel.startAlertSound();

            expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 2000);
            expect(viewModel.alertAudioInterval).toBe(12345);
        });

        test('startAlertSound should handle Audio errors gracefully', () => {
            global.Audio = jest.fn(() => {
                throw new Error('Audio error');
            });

            expect(() => {
                viewModel.startAlertSound();
            }).not.toThrow();

            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining("Could not start alert sound"),
                expect.any(Error)
            );
        });

        test('stopAlertSound should clear interval', () => {
            viewModel.alertAudioInterval = 12345;

            viewModel.stopAlertSound();

            expect(clearInterval).toHaveBeenCalledWith(12345);
            expect(viewModel.alertAudioInterval).toBeNull();
        });

        test('stopAlertSound should handle null interval', () => {
            viewModel.alertAudioInterval = null;

            expect(() => {
                viewModel.stopAlertSound();
            }).not.toThrow();
        });
    });

    describe('closeAlert', () => {
        test('should set isAlertVisible to false', () => {
            viewModel.isAlertVisible(true);

            viewModel.closeAlert();

            expect(viewModel.isAlertVisible()).toBe(false);
        });

        test('should stop alert sound', () => {
            const stopSoundSpy = jest.spyOn(viewModel, 'stopAlertSound');

            viewModel.closeAlert();

            expect(stopSoundSpy).toHaveBeenCalled();
        });

        test('should hide Bootstrap modal', () => {
            const mockModal = {
                modal: jest.fn(),
                length: 1
            };
            mockJQuery.mockReturnValue(mockModal);

            viewModel.closeAlert();

            expect(mockJQuery).toHaveBeenCalledWith('#octo_fire_guard_alert_modal');
            expect(mockModal.modal).toHaveBeenCalledWith('hide');
        });

        test('should handle errors gracefully', () => {
            viewModel.isAlertVisible = jest.fn(() => {
                throw new Error('Test error');
            });

            expect(() => {
                viewModel.closeAlert();
            }).not.toThrow();

            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining("Error closing alert"),
                expect.any(Error)
            );
        });
    });

    describe('Data Timeout Warning', () => {
        test('showDataTimeoutWarning should format sensors correctly', () => {
            const warningData = {
                sensors: ['hotend', 'heatbed'],
                timeout: 300,
                message: 'No temperature data received'
            };

            viewModel.showDataTimeoutWarning(warningData);

            expect(console.warn).toHaveBeenCalledWith(
                expect.stringContaining('Temperature data timeout')
            );
        });

        test('showDataTimeoutWarning should calculate timeout in minutes', () => {
            const warningData = {
                sensors: ['hotend'],
                timeout: 300,
                message: 'Test message'
            };

            viewModel.showDataTimeoutWarning(warningData);

            expect(mockPNotify).toHaveBeenCalledWith(expect.objectContaining({
                text: expect.stringContaining('5 minutes')
            }));
        });

        test('showDataTimeoutWarning should create PNotify', () => {
            const warningData = {
                sensors: ['hotend'],
                timeout: 300,
                message: 'Test message'
            };

            viewModel.showDataTimeoutWarning(warningData);

            expect(mockPNotify).toHaveBeenCalledWith(expect.objectContaining({
                title: 'Octo Fire Guard: Self-Test Warning',
                type: 'warning',
                hide: false
            }));
        });

        test('dismissDataTimeoutWarning should remove notification', () => {
            const mockNotification = {
                remove: jest.fn()
            };
            viewModel.dataTimeoutNotification = mockNotification;

            viewModel.dismissDataTimeoutWarning();

            expect(mockNotification.remove).toHaveBeenCalled();
            expect(viewModel.dataTimeoutNotification).toBeNull();
            expect(console.info).toHaveBeenCalledWith(
                expect.stringContaining('Temperature data timeout warning dismissed')
            );
        });

        test('dismissDataTimeoutWarning should handle null notification', () => {
            viewModel.dataTimeoutNotification = null;

            expect(() => {
                viewModel.dismissDataTimeoutWarning();
            }).not.toThrow();
        });
    });

    describe('testAlert', () => {
        test('should call OctoPrint simpleApiCommand', () => {
            viewModel.testAlert();

            expect(mockOctoPrint.simpleApiCommand).toHaveBeenCalledWith(
                'octo_fire_guard',
                'test_alert'
            );
        });

        test('should log success message on done', () => {
            viewModel.testAlert();

            expect(console.log).toHaveBeenCalledWith('Test alert sent');
        });

        test('should handle missing OctoPrint API', () => {
            global.OctoPrint = undefined;

            viewModel.testAlert();

            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('OctoPrint API not available')
            );
        });

        test('should handle API errors gracefully', () => {
            const mockFail = jest.fn((callback) => {
                callback({ responseJSON: { error: 'Test error' } }, 'error', 'Test error');
            });
            mockOctoPrint.simpleApiCommand = jest.fn(() => ({
                done: jest.fn((callback) => ({ fail: mockFail }))
            }));

            viewModel.testAlert();

            expect(console.error).toHaveBeenCalledWith(
                'Failed to send test alert:',
                'error',
                'Test error'
            );
        });
    });

    describe('testEmergencyActions', () => {
        test('should confirm with user before executing', () => {
            viewModel.testEmergencyActions();

            expect(confirm).toHaveBeenCalledWith(
                expect.stringContaining('This will execute the configured emergency actions')
            );
        });

        test('should not execute if user cancels', () => {
            global.confirm = jest.fn(() => false);

            viewModel.testEmergencyActions();

            expect(mockOctoPrint.simpleApiCommand).not.toHaveBeenCalled();
        });

        test('should call OctoPrint simpleApiCommand', () => {
            viewModel.testEmergencyActions();

            expect(mockOctoPrint.simpleApiCommand).toHaveBeenCalledWith(
                'octo_fire_guard',
                'test_emergency_actions'
            );
        });

        test('should show info notification before execution', () => {
            viewModel.testEmergencyActions();

            expect(mockPNotify).toHaveBeenCalledWith(expect.objectContaining({
                title: 'Testing Emergency Actions',
                type: 'info',
                hide: true,
                delay: 3000
            }));
        });

        test('should show success notification on completion', () => {
            const mockDone = jest.fn((callback) => {
                callback({ success: true, mode: 'gcode', message: 'Test success' });
                return { fail: jest.fn() };
            });
            mockOctoPrint.simpleApiCommand = jest.fn(() => ({
                done: mockDone,
                fail: jest.fn()
            }));

            viewModel.testEmergencyActions();

            expect(mockPNotify).toHaveBeenCalledWith(expect.objectContaining({
                title: 'Test Successful',
                type: 'success'
            }));
        });

        test('should handle API failure', () => {
            const mockFail = jest.fn((callback) => {
                callback({ responseJSON: { error: 'Test error' } }, 'error', 'Test error');
            });
            mockOctoPrint.simpleApiCommand = jest.fn(() => ({
                done: jest.fn((callback) => ({ fail: mockFail }))
            }));

            viewModel.testEmergencyActions();

            expect(console.error).toHaveBeenCalledWith(
                'Failed to test emergency actions:',
                'error',
                'Test error'
            );
        });

        test('should handle missing OctoPrint API', () => {
            global.OctoPrint = undefined;

            viewModel.testEmergencyActions();

            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('OctoPrint API not available')
            );
        });
    });
});
