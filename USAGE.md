# Installation and Usage Guide

## Installation

### Via Plugin Manager (Recommended)

1. Open OctoPrint web interface
2. Navigate to Settings → Plugin Manager
3. Click "Get More..."
4. Enter the following URL in the "... from URL" field:
   ```
   https://github.com/rdar-lab/octo-fire-guard/archive/main.zip
   ```
5. Click "Install"
6. Restart OctoPrint when prompted

### Manual Installation

```bash
pip install https://github.com/rdar-lab/octo-fire-guard/archive/main.zip
```

## Initial Configuration

After installation, configure the plugin:

1. Navigate to Settings → Plugins → Octo Fire Guard
2. Enable temperature monitoring (enabled by default)
3. Set appropriate thresholds:
   - **Hotend Threshold**: Default 250°C (adjust based on your printer and materials)
   - **Heatbed Threshold**: Default 100°C (adjust based on your printer and materials)

### Choosing a Termination Mode

#### GCode Commands (Default)

Best for most users. The plugin will send emergency stop and heater shutdown commands.

**Default commands:**
```gcode
M112        # Emergency stop
M104 S0     # Turn off hotend
M140 S0     # Turn off heatbed
```

**Customization:**
- You can add additional commands specific to your printer
- One command per line
- Commands are sent in order

**Example custom configuration:**
```gcode
M112        # Emergency stop
M104 S0     # Turn off hotend
M140 S0     # Turn off heatbed
M106 S255   # Turn fans to max
G28 X Y     # Home X and Y axes (move away from print)
```

#### PSU Control Mode

Requires the [PSU Control plugin](https://plugins.octoprint.org/plugins/psucontrol/) to be installed and configured.

**Setup:**
1. Install and configure PSU Control plugin
2. Verify PSU Control works correctly (test on/off functionality)
3. In Octo Fire Guard settings, select "PSU Control (Power Off)" as termination mode
4. Verify the PSU plugin name (default: "psucontrol")

**How it works:**
1. Turns off heaters using GCode
2. Sends power-off command to PSU Control plugin
3. Falls back to GCode termination if PSU control fails

## Testing Your Configuration

**IMPORTANT:** Test the alert system before relying on it for safety!

1. Navigate to Settings → Plugins → Octo Fire Guard
2. Click "Test Alert System" button
3. Verify that:
   - Alert popup appears immediately
   - Alert is prominent and visible
   - Audio alert plays (if supported by your browser)
   - You can dismiss the alert by clicking "I UNDERSTAND - Close Alert"

## Setting Appropriate Thresholds

### Hotend Temperature

Consider these factors:
- Maximum temperature rating of your hotend
- Highest temperature materials you print (e.g., ABS ~240°C, Nylon ~260°C)
- Safety margin (recommended 10-20°C above normal max)

**Examples:**
- All-metal hotend, printing ABS: **260-280°C**
- PTFE-lined hotend, printing PLA: **250-260°C**
- High-temp materials: **280-300°C**

### Heatbed Temperature

Consider these factors:
- Maximum temperature rating of your bed
- Highest temperature materials you print (e.g., PLA ~60°C, ABS ~100°C)
- Safety margin (recommended 10-20°C above normal max)

**Examples:**
- Standard heated bed, printing PLA/PETG: **100-110°C**
- High-temp bed, printing ABS/Nylon: **120-130°C**

## How Temperature Monitoring Works

1. **Real-time Monitoring**: Plugin receives temperature updates from OctoPrint (typically every 1-2 seconds)
2. **Threshold Check**: Compares current temperatures against configured thresholds
3. **Alert Trigger**: When threshold exceeded:
   - Logs warning to OctoPrint log
   - Displays prominent alert popup
   - Plays audio alert
   - Executes termination commands
4. **Cooldown Period**: Alert won't re-trigger until temperature drops 10°C below threshold

## Troubleshooting

### Alert Not Appearing

1. Check browser console for errors (F12 → Console)
2. Verify plugin is enabled in Settings
3. Test using "Test Alert System" button
4. Refresh OctoPrint page
5. Try a different browser

### GCode Termination Not Working

1. Check OctoPrint terminal log for sent commands
2. Verify printer is connected when threshold exceeded
3. Check that commands are valid for your printer
4. Some printers may ignore M112; consider adding M410 or printer-specific emergency stop

### PSU Control Not Working

1. Verify PSU Control plugin is installed and enabled
2. Test PSU Control independently
3. Check OctoPrint logs for error messages
4. Verify PSU plugin name matches in settings
5. Plugin will fallback to GCode termination if PSU control fails

### Temperature Not Being Monitored

1. Verify "Enable temperature monitoring" is checked
2. Check that printer is connected and sending temperature updates
3. Look for plugin messages in OctoPrint logs
4. Restart OctoPrint

## Best Practices

1. **Regular Testing**: Test alert system monthly
2. **Appropriate Thresholds**: Don't set too low (false alarms) or too high (reduced protection)
3. **Backup Safety**: This plugin supplements, doesn't replace firmware thermal runaway protection
4. **Physical Monitoring**: Never leave printer completely unattended
5. **Fire Safety**: Keep fire extinguisher nearby, clear flammable materials from printer area
6. **Review Logs**: Periodically check OctoPrint logs for plugin activity

## Integration with Other Safety Plugins

This plugin works well with:
- **Thermal Runaway Protection** (firmware-level)
- **OctoPrint-PrintTimeGenius**: Better time estimates
- **OctoPrint-DisplayLayerProgress**: Monitor print progress
- **OctoPrint-Telegram**: Get notifications remotely

## Advanced Configuration

### Multiple Hotends

The plugin monitors all detected hotends (tool0, tool1, etc.) and uses the same threshold for all. If you need different thresholds per tool, consider:
- Setting threshold to the lowest safe maximum
- Modifying plugin code for per-tool thresholds (advanced)

### Custom Alert Sounds

The plugin includes a built-in beep. To use custom sounds:
1. Modify `octoprint_octo_fire_guard/static/js/octo_fire_guard.js`
2. Replace the audio data URL with your own
3. Or use HTML5 Audio API to play external file

## Uninstallation

1. Navigate to Settings → Plugin Manager
2. Find "Octo Fire Guard" in installed plugins
3. Click trash icon
4. Confirm uninstallation
5. Restart OctoPrint

Or via command line:
```bash
pip uninstall octoprint-octo-fire-guard
```

## Getting Help

- **GitHub Issues**: [https://github.com/rdar-lab/octo-fire-guard/issues](https://github.com/rdar-lab/octo-fire-guard/issues)
- **OctoPrint Community**: [https://community.octoprint.org/](https://community.octoprint.org/)

## License

MIT - See LICENSE file for details
