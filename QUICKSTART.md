# Quick Start Guide

Get up and running with Octo Fire Guard in 5 minutes!

## Step 1: Install the Plugin (2 minutes)

1. Open your OctoPrint web interface
2. Click the **Settings** icon (wrench) → **Plugin Manager**
3. Click **"Get More..."** button
4. Paste this URL in the **"... from URL"** field:
   ```
   https://github.com/rdar-lab/octo-fire-guard/archive/main.zip
   ```
5. Click **Install**
6. Wait for installation to complete
7. Click **Restart** when prompted

## Step 2: Configure Thresholds (2 minutes)

1. After restart, go to **Settings** → **Plugins** → **Octo Fire Guard**
2. Set your hotend threshold:
   - **For PLA/PETG printers**: 250-260°C
   - **For ABS/Nylon printers**: 280-300°C
3. Set your heatbed threshold:
   - **For standard beds**: 100-110°C
   - **For high-temp beds**: 120-130°C
4. Keep termination mode as **"GCode Commands"** (default is safe)
5. Click **Save**

## Step 3: Test the Alert (1 minute)

1. Still in the Octo Fire Guard settings
2. Click **"Test Alert System"** button
3. You should see:
   - ✓ Large red alert popup
   - ✓ "TEMPERATURE ALERT!" message
   - ✓ Alert beep sound
4. Click **"I UNDERSTAND - Close Alert"** to dismiss
5. If alert appears correctly, you're done! ✅

## You're Protected! 🛡️

The plugin is now:
- ✓ Monitoring your hotend temperature
- ✓ Monitoring your heatbed temperature
- ✓ Ready to trigger emergency shutdown if thresholds exceeded
- ✓ Protecting your printer 24/7

## What Happens in an Emergency?

If temperature exceeds threshold:
1. 🔴 Large alert pops up immediately
2. 🔊 Beep sound plays
3. 🛑 Emergency stop command sent (M112)
4. ❄️ Heaters turned off (M104 S0, M140 S0)
5. 📝 Event logged in OctoPrint logs

## Next Steps

### Optional: Advanced Configuration

Want more control? Check out:
- **[USAGE.md](USAGE.md)** - Detailed configuration guide
- **[EXAMPLES.md](EXAMPLES.md)** - Configuration examples for different printers
- **[FEATURES.md](FEATURES.md)** - Complete feature list

### Optional: PSU Control Integration

Want to cut power completely in an emergency?
1. Install **PSU Control** plugin
2. Configure PSU Control to control your printer's power
3. In Octo Fire Guard settings, change mode to **"PSU Control (Power Off)"**
4. Test PSU Control independently first!

## Troubleshooting

### Alert Doesn't Appear
- Refresh OctoPrint page (Ctrl+F5)
- Check browser console for errors (F12)
- Verify plugin is enabled in settings

### Emergency Stop Doesn't Work
- Check printer is connected when threshold exceeded
- Verify commands are valid for your printer
- Check OctoPrint Terminal tab for sent commands

### Need Help?
- Check **[USAGE.md](USAGE.md)** for detailed troubleshooting
- Open an issue on [GitHub](https://github.com/rdar-lab/octo-fire-guard/issues)

## Safety Reminders ⚠️

- ✓ This plugin is a **safety supplement**, not a replacement for supervision
- ✓ Never leave your printer **completely unattended**
- ✓ Ensure your printer firmware has **thermal runaway protection**
- ✓ Keep a **fire extinguisher** nearby
- ✓ Test the plugin regularly (monthly recommended)

---

**That's it! You're protected in 5 minutes!** 🎉

For more details, see [README.md](README.md)
