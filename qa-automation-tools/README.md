# QA Automation Tools

A comprehensive set of quality assurance automation tools for web applications, including accessibility testing, API validation, performance testing, and battery consumption simulation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Accessibility Testing](#accessibility-testing)
  - [Response Testing](#response-testing)
  - [Performance Testing](#performance-testing)
  - [Battery Simulation Testing](#battery-simulation-testing)
  - [Running All Tests](#running-all-tests)
- [Reports](#reports)
- [Extending the Framework](#extending-the-framework)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This QA automation toolkit provides a set of Python-based tools for testing various aspects of web applications:

1. **Accessibility Testing**: Automated tests to ensure your web application complies with WCAG accessibility standards.
2. **Response Testing**: Tools to validate website responses, formats, and performance (currently tests the homepage).
3. **Performance Testing**: Measure page load times and response times.
4. **Battery Simulation**: Simulate user interactions and measure battery consumption.

## Features

- **Modular Design**: Each testing tool can be used independently or together.
- **Comprehensive Reports**: Generate detailed reports in JSON and HTML formats.
- **Configurable**: Easily customize tests for your specific application.
- **Cross-Browser Support**: Test on Chrome, Firefox, and other browsers.
- **Visualization**: Generate charts and graphs for performance and battery metrics.

## Installation

1. Clone this repository or copy the `qa-automation-tools` directory to your project.

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

   **Note on Python 3.13+ Compatibility**:
   The requirements.txt file uses flexible version specifications and conditional dependencies to ensure compatibility with Python 3.13+. Key compatibility features:
   
   - Gevent is only installed on Python versions below 3.13
   - Different versions of matplotlib and numpy are installed based on your Python version
   - Version constraints are more flexible (using >= instead of ==) to allow for compatible versions
   
   If you still encounter installation issues:
   ```bash
   pip install -r requirements.txt --use-pep517
   ```
   
   All tools will work even if some packages fail to install, with graceful fallbacks for missing dependencies.

3. Make sure you have Chrome or Firefox installed on your system.

## Usage

### Accessibility Testing

The accessibility testing tool uses the axe-core library to check your web application for WCAG compliance issues.

```bash
python test_accessibility.py --url http://your-website.com
```

Options:
- `--url`: URL of the website to test (default: http://localhost:3000)
- `--browser`: Browser to use (chrome or firefox, default: chrome)
- `--level`: WCAG compliance level to check (a, aa, or aaa, default: aa)

### Response Testing

The API testing tool validates your web application's responses and formats.

```bash
python test_api.py --url http://your-website.com
```

Options:
- `--url`: Base URL of the website to test (default: http://localhost:3000)

Note: The API test currently tests the homepage (root endpoint) of your website. If you have actual API endpoints, you'll need to modify the test script to test those specific endpoints.

### Performance Testing

The performance testing tool measures page load times and API response times.

```bash
python test_performance.py --url http://your-website.com
```

Options:
- `--url`: URL of the website to test (default: http://localhost:3000)
- `--requests`: Number of requests to make (default: 10)
- `--delay`: Delay between requests in seconds (default: 1)

### Battery Simulation Testing

The battery simulation tool simulates user interactions and measures system resource usage. It uses an intelligent approach to interact with your website while minimizing errors.

```bash
python test_battery_simulation.py --url http://your-website.com
```

Options:
- `--url`: URL of the website to test (default: http://localhost:3000)
- `--duration`: Duration of the simulation in seconds (default: 60)
- `--browser`: Browser to use (chrome or firefox, default: chrome)

Key Features:
- Smart element selection that filters for visible and enabled elements
- JavaScript-based clicking for better reliability with overlapping elements
- Retry mechanism for handling stale element references
- Detailed logging of actions performed during the simulation
- Comprehensive resource usage metrics (CPU, memory, battery)

### Running All Tests

You can run all tests at once using the `run_all_tests.py` script:

```bash
python run_all_tests.py --url http://your-website.com
```

Options:
- `--url`: URL of the website to test (default: http://localhost:3000)
- `--accessibility`: Run only accessibility tests
- `--api`: Run only response tests
- `--performance`: Run only performance tests
- `--battery`: Run only battery simulation tests
- `--all`: Run all tests (default if no specific tests are selected)

## Reports

All test reports are saved in the `reports` directory:

- `accessibility_report.json` and `accessibility_report.html`: Accessibility test results
  - Look for "violations" in the report to identify accessibility issues
  - Common violations include contrast issues, missing alt text, and keyboard navigation problems
  - The HTML report provides visual indicators of where issues occur on the page
- `api_validation_report.json`: Response test results
- `performance_report.json`: Performance test results
- `battery_test_report.json`: Battery simulation test results
  - Contains information about CPU usage, memory usage, and battery drain
  - Includes a list of actions performed during the simulation
  - The test uses smart element selection to minimize errors
  - Uses JavaScript click and retry mechanisms for more reliable interaction
- Charts and graphs for performance and battery metrics

## Extending the Framework

### Adding New Tests

1. Create a new test file following the pattern of existing tests.
2. Import the necessary modules and classes.
3. Create a test class that encapsulates your test logic.
4. Add a main function to run the test independently.
5. Update `run_all_tests.py` to include your new test.

### Customizing Existing Tests

Each test module is designed to be easily customizable:

- Modify the test parameters in the main function.
- Extend the test classes to add new functionality.
- Override methods to change behavior.

## Best Practices

1. **Run tests regularly**: Integrate these tests into your CI/CD pipeline.
2. **Test early and often**: Run tests during development, not just before release.
3. **Fix accessibility issues**: Address accessibility violations as they are found.
   - Common issues include contrast problems between text and background colors
   - Use tools like the Chrome DevTools color picker to check contrast ratios
   - Aim for a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text
4. **Monitor performance trends**: Track performance metrics over time to identify regressions.
5. **Test on multiple devices**: Use different configurations to ensure broad compatibility.

## Troubleshooting

### Common Issues

1. **WebDriver errors**: Make sure you have the latest version of Chrome or Firefox installed.
2. **Package installation errors**:
   - Try using `pip install -r requirements.txt --use-pep517`
   - For specific packages: `pip install package_name --no-binary :all:`
   - The tools have fallbacks for missing packages
3. **Permission errors**: Make sure the script has permission to write to the `reports` directory.
4. **Connection errors**: Verify that the application is running at the specified URL.
5. **API test 404 errors**: The API test is configured to test the root endpoint ("/") of your website. If you're getting 404 errors, make sure your website is running and accessible at the specified URL.
6. **Battery simulation interaction**:
   - The battery simulation test has been improved to minimize errors by using smart element selection
   - It now filters for visible and enabled elements before attempting to click
   - Uses JavaScript click as the primary method for better reliability
   - Implements a retry mechanism for handling stale element references
   - If you still see occasional errors, these are normal and don't affect the test results
7. **Python 3.13+ compatibility issues**:
   - The requirements file uses conditional dependencies for better compatibility
   - All tools will work with reduced functionality if certain packages can't be installed
   - Consider using a virtual environment with Python 3.11 or 3.12 for full functionality

### Getting Help

If you encounter issues not covered here, please:

1. Check the error message for specific details.
2. Verify that your environment meets all prerequisites.
3. Try running individual test modules to isolate the issue.