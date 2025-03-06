[![PyPI version](https://badge.fury.io/py/qmetry-pytest.svg)](https://badge.fury.io/py/qmetry-pytest)
[![codecov](https://codecov.io/github/prashanth-sams/qmetry-pytest/graph/badge.svg?token=WVRR4PU0VS)](https://codecov.io/github/prashanth-sams/qmetry-pytest)
[![PyPI Downloads](https://static.pepy.tech/badge/qmetry-pytest)](https://pepy.tech/projects/qmetry-pytest)

# qmetry-pytest
A PyTest plugin that provides seamless integration with QMetry Test Management Platform.

<p align="left">
  <img width="435" alt="qmetry" src="https://github.com/user-attachments/assets/452a8748-7987-4443-b6d0-d43a7b72b96d" />
</p>

## Features

- Automatically uploads test results to QMetry
- Generates test cycles and updates test case statuses seamlessly
- Supports JUnit XML reports for Automation API
- Supports Cucumber JSON reports for Automation API

## Installation

```
pip install qmetry-pytest
```

## Configuration

You'll need to create a qmetry.properties file in your project root.

#### Default and Mandatory Properties:
```
qmetry.enabled=true
qmetry.url=<your_qmetry_url>
qmetry.authorization=<your_authorization>
```

### Automation API

#### Mandatory Properties:
```
qmetry.automation.enabled=true
qmetry.automation.apikey=<your_api_key>
qmetry.automation.resultfile=<your_report_path/filename.xml/json>
```

#### Optional Properties:
```
qmetry.automation.payload.format=<junit/cucumber>
qmetry.automation.payload.attachFile=true
qmetry.automation.payload.isZip=false
qmetry.automation.payload.environment=<env_label>
qmetry.automation.payload.build=<build_no>
qmetry.automation.payload.fields.testCycle.labels=<label>
qmetry.automation.payload.fields.testCycle.status=Done
qmetry.automation.payload.fields.testCycle.summary=<test_cycle_summary>
qmetry.automation.payload.fields.testCycle.customFields=<Environment:DEV>
qmetry.automation.payload.fields.testCase.labels=<label>
qmetry.automation.payload.fields.testCase.status=Done
```

## Test Example

```
import pytest

def test_example():
    assert True

@pytest.mark.qid("TC-124")
def test_another_example():
    assert 1 + 1 == 2
```

## Test Execution

```
pytest --qmetry
```

### To generate XML report before upload

Note: Skip this section if you are using the Cucumber framework

```
pytest --qmetry --junitxml=report/results.xml
```

## Best Practices

- No markers are required for the automation flow.
- Ensure secure authentication and keep the configuration updated in `qmetry.properties`.
- Remember to include `--qmetry` as a command-line argument during test execution.
