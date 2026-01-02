# Example Configuration

This file shows example configurations for different printer setups.

## Basic PLA Printer (PTFE Hotend)

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 250°C
  Heatbed Threshold: 80°C
  Termination Mode: GCode Commands
  Termination GCode:
    M112
    M104 S0
    M140 S0
```

## High-Temperature Printer (All-Metal Hotend)

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 300°C
  Heatbed Threshold: 130°C
  Termination Mode: GCode Commands
  Termination GCode:
    M112
    M104 S0
    M140 S0
    M106 S255  # Max fans for cooling
```

## Printer with PSU Control

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 260°C
  Heatbed Threshold: 110°C
  Termination Mode: PSU Control (Power Off)
  PSU Plugin Name: psucontrol
```

## Conservative Safety Settings

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 240°C  # Lower threshold for safety
  Heatbed Threshold: 90°C   # Lower threshold for safety
  Termination Mode: GCode Commands
  Termination GCode:
    M112
    M104 S0
    M140 S0
    M84    # Disable steppers
    M107   # Turn off part cooling fan
```

## Custom Emergency Response

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 280°C
  Heatbed Threshold: 120°C
  Termination Mode: GCode Commands
  Termination GCode:
    M112              # Emergency stop
    M104 S0           # Turn off hotend
    M140 S0           # Turn off heatbed
    M106 S255         # Max fans
    G91               # Relative positioning
    G1 Z10 F300       # Lift Z 10mm
    G90               # Absolute positioning
    G28 X Y           # Home X and Y
    M84               # Disable motors
```

## Prusa Printer Example

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 280°C
  Heatbed Threshold: 110°C
  Termination Mode: GCode Commands
  Termination GCode:
    M112
    M104 S0
    M140 S0
```

## Creality Ender 3 Example

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 260°C
  Heatbed Threshold: 100°C
  Termination Mode: GCode Commands
  Termination GCode:
    M112
    M104 S0
    M140 S0
    M106 S255
```

## Testing Configuration

For testing the plugin without actual risk:

```yaml
Settings → Plugins → Octo Fire Guard:
  Enable temperature monitoring: ✓
  Hotend Threshold: 999°C  # Won't trigger during normal operation
  Heatbed Threshold: 999°C  # Won't trigger during normal operation
  Termination Mode: GCode Commands
  Termination GCode:
    M117 Test Alert  # Just display message
```

Then use the "Test Alert System" button to verify the UI works correctly.
