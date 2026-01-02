# Octo Fire Guard

[![Unit Tests](https://github.com/rdar-lab/octo-fire-guard/actions/workflows/tests.yml/badge.svg)](https://github.com/rdar-lab/octo-fire-guard/actions/workflows/tests.yml)

An OctoPrint plugin that monitors printer temperatures in real-time to prevent fire hazards. The plugin watches both hotend and heatbed temperatures and triggers emergency shutdown procedures when configurable thresholds are exceeded.

## Features

- **Real-time Temperature Monitoring**: Continuously monitors hotend and heatbed temperatures via OctoPrint's temperature data stream
- **Dual Threshold Configuration**: Separate configurable thresholds for hotend (default: 250°C) and heatbed (default: 100°C)
- **Immediate Alert System**: Displays a prominent alert popup in the OctoPrint interface when thresholds are exceeded
- **Flexible Emergency Response**: Choose between two termination modes:
  - **GCode Commands**: Execute custom GCode commands (default: M112 emergency stop + heater shutdown)
  - **PSU Control Integration**: Turn off power entirely via PSU Control plugin
- **User-Friendly Interface**: Easy-to-use settings panel with test functionality
- **Audio Alerts**: Plays an alert sound when temperature threshold is exceeded

## Installation

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html) or manually using this URL:

```
https://github.com/rdar-lab/octo-fire-guard/archive/main.zip
```

## Configuration

After installation, configure the plugin in OctoPrint Settings → Plugins → Octo Fire Guard:

### Temperature Thresholds

- **Hotend Threshold**: Maximum safe temperature for the hotend in °C (default: 250°C)
- **Heatbed Threshold**: Maximum safe temperature for the heatbed in °C (default: 100°C)

### Termination Mode

Choose how the plugin responds when a threshold is exceeded:

#### GCode Commands Mode
Execute custom GCode commands to handle the emergency. Default commands:
```gcode
M112        # Emergency stop
M104 S0     # Turn off hotend
M140 S0     # Turn off heatbed
```

You can customize these commands to suit your printer's requirements.

#### PSU Control Mode
Integrates with the [PSU Control plugin](https://plugins.octoprint.org/plugins/psucontrol/) to turn off power completely. This mode:
1. Turns off heaters using GCode
2. Signals the PSU Control plugin to cut power

**Note**: Requires the PSU Control plugin to be installed and configured.

## How It Works

1. The plugin subscribes to OctoPrint's temperature callback system
2. Every time temperature data is received from the printer:
   - Checks if any hotend temperature exceeds the configured threshold
   - Checks if the heatbed temperature exceeds the configured threshold
3. When a threshold is exceeded:
   - Logs a warning message
   - Displays a prominent alert popup in the OctoPrint UI
   - Plays an audio alert (if supported by the browser)
   - Executes the configured termination commands
4. The alert remains until the user acknowledges it
5. Temperature monitoring continues, with a cooldown period to prevent repeated alerts

## Testing

Use the "Test Alert System" button in the settings to verify that alerts display correctly without triggering an actual emergency.

## Safety Considerations

- **This plugin is a safety feature, not a replacement for proper printer supervision**
- Set thresholds appropriate for your printer and materials
- Regularly test the plugin to ensure it's functioning correctly
- Ensure your printer's firmware has proper thermal runaway protection
- For PSU Control mode, verify your PSU Control setup works correctly before relying on it

## Requirements

- OctoPrint 1.4.0 or higher
- Python 2.7 or 3.x
- For PSU Control mode: PSU Control plugin installed and configured

## Development

### Plugin Structure

```
octo-fire-guard/
├── octoprint_octo_fire_guard/
│   ├── __init__.py              # Main plugin logic
│   ├── static/
│   │   ├── css/
│   │   │   └── octo_fire_guard.css
│   │   └── js/
│   │       └── octo_fire_guard.js
│   └── templates/
│       └── octo_fire_guard_settings.jinja2
├── tests/
│   ├── __init__.py
│   ├── test_octo_fire_guard.py  # Comprehensive unit tests
│   └── README.md                # Test documentation
├── setup.py
├── run_tests.py                 # Test runner script
├── MANIFEST.in
├── LICENSE
└── README.md
```

### Key Components

- **Temperature Monitoring**: Uses OctoPrint's `octoprint.comm.protocol.temperatures.received` hook
- **Alert System**: Sends plugin messages to the frontend for display
- **Emergency Response**: Executes termination commands via printer commands or plugin messages

### Testing

The plugin includes a comprehensive test suite with **38 unit tests** covering all major functionality.

To run the tests:

```bash
python3 run_tests.py
```

Or run tests directly:

```bash
python3 tests/test_octo_fire_guard.py -v
```

See [tests/README.md](tests/README.md) for detailed information about the test suite.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have suggestions, please [open an issue](https://github.com/rdar-lab/octo-fire-guard/issues) on GitHub.
