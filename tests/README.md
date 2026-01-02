# Unit Tests for Octo Fire Guard

This directory contains comprehensive unit tests for the Octo Fire Guard OctoPrint plugin.

## Running the Tests

To run all tests:

```bash
python3 tests/test_octo_fire_guard.py
```

Or with verbose output:

```bash
python3 tests/test_octo_fire_guard.py -v
```

Using unittest discovery:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Test Coverage

The test suite includes **38 comprehensive tests** covering:

### Plugin Initialization (3 tests)
- Plugin state initialization
- Default settings configuration
- Settings version management

### Asset & Template Configuration (2 tests)
- JavaScript and CSS asset loading
- Template configuration

### API Commands (2 tests)
- API command registration
- Test alert functionality

### Temperature Monitoring (12 tests)
- Safe temperature handling
- Hotend threshold exceeded detection
- Heatbed threshold exceeded detection
- Multiple tool monitoring
- Threshold reset after cooldown
- Monitoring enable/disable toggle
- None/invalid temperature handling
- Empty temperature data handling
- Boundary condition testing
- Multiple simultaneous threshold breaches

### Emergency Shutdown System (10 tests)
- GCode termination mode
- Custom GCode commands
- PSU control termination mode
- PSU plugin fallback mechanisms
- Exception handling
- Alternative PSU method names
- Unknown termination mode handling
- Whitespace and empty line handling

### Plugin Integration (2 tests)
- Complete emergency workflow for hotend
- Complete emergency workflow for heatbed

### Plugin Hooks (2 tests)
- Plugin load function
- Plugin implementation registration

### Update System (1 test)
- Software update configuration

### Edge Cases (5 tests)
- Rapid temperature changes
- Exact boundary conditions
- Cooldown threshold precision
- Empty data handling
- Invalid data formats

## Test Architecture

The tests use Python's built-in `unittest` framework with `unittest.mock` for mocking OctoPrint dependencies. The test structure includes:

1. **Mock Setup**: OctoPrint and Flask modules are mocked to allow testing without full OctoPrint installation
2. **Test Fixtures**: Each test class has a `setUp` method that initializes plugin instances with mocked dependencies
3. **Isolation**: Tests are isolated and don't depend on external state
4. **Comprehensive Coverage**: Tests cover happy paths, error conditions, and edge cases

## Test Classes

### TestOctoFireGuardPlugin
Main test class covering all core plugin functionality including settings, temperature monitoring, and emergency shutdown procedures.

### TestPluginHooks
Tests for OctoPrint plugin hook registration and implementation loading.

### TestPluginIntegration
Integration tests that verify complete end-to-end workflows from temperature detection through emergency shutdown and reset.

## Dependencies

The tests require Python 3.x with the following standard library modules:
- `unittest` (built-in)
- `unittest.mock` (built-in)
- No external dependencies required!

## Contributing

When adding new features to the plugin, please:
1. Add corresponding unit tests
2. Ensure all existing tests pass
3. Maintain test isolation (no shared state between tests)
4. Mock external dependencies appropriately
