# Plugin Features Summary

## Overview
Octo Fire Guard is a safety plugin for OctoPrint that monitors temperature sensors in real-time and triggers emergency shutdown when thresholds are exceeded. It also includes self-test monitoring to ensure the plugin is functioning correctly.

## Key Components

### 1. Settings Panel
Located in: **OctoPrint Settings → Plugins → Octo Fire Guard**

Features:
- Enable/disable monitoring checkbox
- Enable/disable self-test monitoring checkbox
- Temperature data timeout setting
- Hotend threshold input (°C)
- Heatbed threshold input (°C)
- Termination mode selector (GCode or PSU Control)
- GCode commands textarea (for GCode mode)
- PSU plugin name input (for PSU mode)
- Test Alert button

### 2. Temperature Monitoring
- Continuously monitors via OctoPrint's temperature callback system
- Checks every temperature update from printer (typically 1-2 seconds)
- Monitors all hotend tools (tool0, tool1, etc.)
- Monitors heatbed temperature
- Cooldown logic prevents alert spam (10°C hysteresis)
- Tracks last received data timestamp for self-test monitoring

### 3. Self-Test Monitoring
- Background timer checks every 30 seconds for temperature data
- Detects if printer is connected but no data received
- Configurable timeout period (default: 5 minutes)
- Issues warning notification when timeout occurs
- Automatically clears warning when data resumes
- Only monitors when printer is operational

### 4. Alert System
When threshold exceeded:
- **Large Modal Popup**: Red-themed, prominent alert
- **Alert Content**:
  - "TEMPERATURE ALERT!" header
  - Emergency message
  - Sensor type (hotend/heatbed)
  - Current temperature
  - Threshold temperature
  - Warning about emergency shutdown
- **Audio Alert**: Plays beep sound
- **Blinking Animation**: Visual attention grabber
- **Acknowledgment Required**: User must click to dismiss

When self-test detects missing data:
- **Warning Notification**: Yellow-themed notification
- **Content**: Information about missing sensors and timeout period
- **Non-intrusive**: Doesn't block UI but remains visible

### 5. Emergency Shutdown
**GCode Mode** (Default):
- Sends M112 (emergency stop)
- Sends M104 S0 (turn off hotend)
- Sends M140 S0 (turn off heatbed)
- Customizable command sequence

**PSU Control Mode**:
- Turns off heaters with GCode
- Calls PSU plugin to cut power
- Falls back to GCode if PSU control fails

## File Structure

```
octo-fire-guard/
├── setup.py                    # Plugin package definition
├── MANIFEST.in                 # Package manifest
├── README.md                   # Main documentation
├── USAGE.md                    # Detailed usage guide
├── EXAMPLES.md                 # Configuration examples
├── LICENSE                     # AGPLv3 license
└── octoprint_octo_fire_guard/  # Plugin package
    ├── __init__.py             # Main plugin logic (237 lines)
    ├── static/
    │   ├── css/
    │   │   └── octo_fire_guard.css     # Alert styling
    │   └── js/
    │       └── octo_fire_guard.js      # Frontend logic
    └── templates/
        └── octo_fire_guard_settings.jinja2  # Settings UI
```

## Plugin Hooks Used

1. **octoprint.comm.protocol.temperatures.received**
   - Receives temperature data in real-time
   - Called every time printer sends temperature update
   - Returns: parsed_temperatures (passthrough, no modification)

2. **octoprint.plugin.softwareupdate.check_config**
   - Enables automatic update checking
   - Points to GitHub releases

## Plugin Mixins Used

1. **SettingsPlugin**: Provides settings storage and defaults
2. **AssetPlugin**: Serves CSS and JavaScript files
3. **TemplatePlugin**: Renders settings template
4. **StartupPlugin**: Logs startup information
5. **SimpleApiPlugin**: Handles test alert API command

## User Workflow

1. **Installation**:
   - Install via Plugin Manager URL
   - Restart OctoPrint

2. **Configuration**:
   - Navigate to Settings → Plugins → Octo Fire Guard
   - Set appropriate thresholds
   - Choose termination mode
   - Test with "Test Alert System" button

3. **Operation**:
   - Plugin monitors automatically when enabled
   - No user interaction needed during normal operation
   - Alert appears if threshold exceeded
   - User acknowledges alert

4. **Emergency Response**:
   - Alert displayed immediately
   - Termination commands executed
   - Log entries created
   - User must investigate printer

## Testing Features

- **Test Alert Button**: Triggers demo alert without emergency
- **High Threshold Testing**: Set thresholds to 999°C for normal printing
- **Log Monitoring**: Check OctoPrint logs for plugin activity
- **PSU Test**: Verify PSU control works before relying on it

## Safety Features

- **Cooldown Period**: Prevents alert spam with 10°C hysteresis
- **Fallback Logic**: PSU mode falls back to GCode if PSU unavailable
- **Logging**: All events logged for troubleshooting
- **Visual + Audio**: Multiple alert modalities
- **Mandatory Acknowledgment**: User must dismiss alert
- **Separate Thresholds**: Different limits for hotend and bed

## Browser Compatibility

- **Tested with**: Modern browsers (Chrome, Firefox, Edge, Safari)
- **Requirements**: JavaScript enabled, HTML5 Audio support (optional)
- **Responsive**: Modal adapts to screen size

## Performance Considerations

- **Lightweight**: Minimal CPU impact
- **Efficient**: Uses OctoPrint's existing temperature system
- **Non-blocking**: Temperature monitoring doesn't slow communication
- **Smart Alerts**: Cooldown prevents repeated triggers

## Future Enhancement Ideas

(Not implemented, but possible extensions)
- Per-tool threshold configuration
- Temperature trend analysis
- Email/SMS notifications
- Temperature logging to file
- Customizable alert sounds
- Multi-language support
- Integration with other notification plugins
- Temperature history graphs
