# Unit Tests for Octo Fire Guard

This directory contains comprehensive unit tests for both the Python backend and JavaScript frontend of the Octo Fire Guard OctoPrint plugin.

## Test Files

- **test_octo_fire_guard.py** - Python backend unit tests (84 tests)
- **octo_fire_guard.test.js** - JavaScript frontend unit tests (43 tests)

## Running the Tests

### Python Tests

To run all Python tests:

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

Or use the convenience script from the project root:

```bash
python3 run_tests.py
```

### JavaScript Tests

To run all JavaScript tests:

```bash
npm test
```

To run tests with coverage:

```bash
npm run test:coverage
```

To run tests in watch mode (for development):

```bash
npm run test:watch
```

**Note**: You need to install Node.js dependencies first:

```bash
npm install
```

## Python Test Coverage

The Python test suite includes **84 comprehensive tests** covering:

### Plugin Initialization (3 tests)
- Plugin state initialization
- Default settings configuration
- Settings version management

### Asset & Template Configuration (2 tests)
- JavaScript and CSS asset loading
- Template configuration

### API Commands (8 tests)
- API command registration
- Test alert functionality
- Test emergency actions (GCode mode, PSU mode, permission checks)
- Error handling and validation
- Unknown termination mode handling

### Temperature Monitoring (30+ tests)
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
- New temperature format support (T0, T1, B)
- Mixed format handling

### Emergency Shutdown System (12 tests)
- GCode termination mode
- Custom GCode commands
- PSU control termination mode
- PSU plugin fallback mechanisms
- Exception handling
- Alternative PSU method names
- Unknown termination mode handling
- Whitespace and empty line handling

### Temperature Data Monitoring (15 tests)
- Data timeout detection for hotend and heatbed
- Self-test monitoring functionality
- Warning message generation
- Timeout warning dismissal
- Data resume detection
- Printer operational state handling

### Printer Reconnection Handling (5 tests)
- State reset on printer connection
- Thread-safe state management
- Post-reconnection behavior

### Debug Logging (10 tests)
- Comprehensive debug message validation
- Logging at different severity levels

### Plugin Integration (2 tests)
- Complete emergency workflow for hotend
- Complete emergency workflow for heatbed

### Plugin Hooks (2 tests)
- Plugin load function
- Plugin implementation registration

### Update System (1 test)
- Software update configuration

## JavaScript Test Coverage

The JavaScript test suite includes **43 comprehensive tests** covering:

### ViewModel Initialization (2 tests)
- Default value initialization
- Alert sound data configuration

### Settings Management (3 tests)
- Settings loading from OctoPrint
- Missing settings handling
- Error handling during settings load

### Event Handlers (3 tests)
- Test alert button event attachment
- Test emergency button event attachment
- Missing button handling

### Plugin Message Handling (4 tests)
- Message filtering by plugin name
- Temperature alert message handling
- Data timeout warning handling
- Data timeout cleared handling

### Alert System (5 tests)
- Alert observable updates
- Bootstrap modal display
- Alert sound triggering
- PNotify notification creation
- Error handling

### Alert Sound Controls (6 tests)
- Sound start/stop functionality
- Continuous beeping interval setup
- Audio error handling
- Interval cleanup

### Alert Close Functionality (4 tests)
- Alert visibility toggle
- Sound stopping
- Modal hiding
- Error handling

### Data Timeout Warning (5 tests)
- Sensor name formatting
- Timeout duration calculation
- Notification creation
- Notification dismissal
- Null notification handling

### API Interactions (8 tests)
- Test alert API calls
- Test emergency actions API calls
- User confirmation handling
- Success/failure notification display
- OctoPrint API availability checks
- Error handling

## Test Architecture

### Python Tests

The Python tests use Python's built-in `unittest` framework with `unittest.mock` for mocking. The test structure includes:

1. **Mock Setup**: OctoPrint and Flask modules are mocked to allow testing without full OctoPrint installation
2. **Test Fixtures**: Each test class has a `setUp` method that initializes plugin instances with mocked dependencies
3. **Isolation**: Tests are isolated and don't depend on external state
4. **Comprehensive Coverage**: Tests cover happy paths, error conditions, and edge cases

### JavaScript Tests

The JavaScript tests use [Jest](https://jestjs.io/) testing framework with JSDOM environment. The test structure includes:

1. **Mock Setup**: jQuery, Knockout, OctoPrint API, PNotify, and Audio are mocked
2. **Test Fixtures**: Each test suite has a `beforeEach` hook that sets up fresh mocks
3. **ViewModel Implementation**: A mock ViewModel implementation that mimics the real behavior
4. **Isolation**: Tests are isolated with automatic cleanup via `afterEach`

## Dependencies

### Python Tests
- Python 3.8 or higher
- `unittest` (built-in)
- `unittest.mock` (built-in)
- No external dependencies required!

### JavaScript Tests
- Node.js 20 or higher
- Jest 29.7.0
- jest-environment-jsdom 29.7.0

Install JavaScript dependencies:
```bash
npm install
```

## Continuous Integration

Both Python and JavaScript tests are automatically run in GitHub Actions on every push and pull request. The CI workflow:

- **Python Tests**: Run on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- **JavaScript Tests**: Run on Node.js 20 with full coverage reporting

See `.github/workflows/tests.yml` for the complete CI configuration.

## Contributing

When adding new features to the plugin, please:
1. Add corresponding unit tests for both Python and JavaScript code
2. Ensure all existing tests pass
3. Maintain test isolation (no shared state between tests)
4. Mock external dependencies appropriately
5. Run both test suites locally before pushing
