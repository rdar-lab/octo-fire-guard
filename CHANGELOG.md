# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-02

### Added
- Initial release of Octo Fire Guard plugin
- Real-time temperature monitoring via OctoPrint's temperature callback system
- Separate configurable thresholds for hotend (default: 250°C) and heatbed (default: 100°C)
- Prominent modal alert popup when temperature thresholds are exceeded
- Audio alert notification when threshold exceeded
- Two termination modes:
  - GCode Commands: Execute custom GCode on emergency (default: M112, M104 S0, M140 S0)
  - PSU Control: Turn off power via PSU Control plugin integration
- Settings panel with intuitive configuration interface
- Test Alert functionality to verify alert system works correctly
- Cooldown logic with 10°C hysteresis to prevent alert spam
- Comprehensive logging of all temperature events and actions
- Fallback mechanism: PSU mode falls back to GCode if PSU control unavailable
- Support for multiple hotend monitoring (tool0, tool1, etc.)
- Blinking visual alert animation for critical warnings
- Comprehensive documentation:
  - README.md with feature overview
  - USAGE.md with detailed usage instructions
  - EXAMPLES.md with configuration examples
  - FEATURES.md with technical details
- Python 2.7 and 3.x compatibility
- OctoPrint 1.4.0+ support

### Security
- No security vulnerabilities detected in CodeQL scan
- Proper input sanitization via OctoPrint settings system
- Safe command execution through OctoPrint's printer interface
- No code injection vulnerabilities

### Developer Notes
- Plugin uses standard OctoPrint plugin architecture
- Implements SettingsPlugin, AssetPlugin, TemplatePlugin, StartupPlugin, and SimpleApiPlugin mixins
- Uses octoprint.comm.protocol.temperatures.received hook for temperature monitoring
- Frontend uses Knockout.js for reactive UI
- CSS provides prominent, attention-grabbing alert styling

## [Unreleased]

### Fixed
- **UI Customizer Compatibility**: Fixed conflicts with "UI Customizer (0.1.9.91)" plugin
  - Removed strict element bindings that caused Save button spinner to hang
  - Added manual modal binding in `onAfterBinding` lifecycle hook for better DOM manipulation resilience
  - Added defensive checks in `testAlert` function to handle cases where OctoPrint API might not be fully loaded
  - Plugin now works correctly when UI Customizer or other DOM-modifying plugins are active
  - Both "Save" button and "Test Alert System" functionality now work reliably with UI Customizer

### Technical Details
- Changed viewModel registration from strict element array `["#settings_plugin_octo_fire_guard", "#octo_fire_guard_alert_modal"]` to empty array `[]`
- Implemented `onAfterBinding` lifecycle hook for manual Knockout.js binding of alert modal
- Enhanced error handling in API command failures with more descriptive error messages

### Potential Future Enhancements
- Per-tool threshold configuration
- Temperature trend analysis
- Email/SMS notification integration
- Historical temperature logging
- Custom alert sound uploads
- Multi-language support
- Integration with additional notification plugins
- Temperature history visualization
