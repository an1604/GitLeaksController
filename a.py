import uuid













import boto3




import pytest






















@pytest.fixture




def execution_id():




    """Returns a random uuid4 string."""




    return str(uuid.uuid4())






















@pytest.fixture




def s3_mock_client():




    """We run the S3 mock server on localhost:9090."""




    return boto3.client(




        's3',




        endpoint_url='http://localhost:9090',




        aws_access_key_id='test',
@jit-ci-bandit jit-ci-bandit bot 15 hours ago
Security control: Static Code Analysis Checkmarx

Use Of Hardcoded Password

The application uses the hard-coded password "test" for authentication purposes, either using it to verify users' identities, or to access another remote system. This password at line 111 of /galgal.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding the application.

Severity: LOW

Jit Bot commands and options (e.g., ignore issue)
@an1604	Reply...
@jit-ci-bandit jit-ci-bandit bot 15 hours ago
Security control: Static Code Analysis Checkmarx

Hardcoded Aws Credentials

AWS credentials are hardcoded in "test", in the file /galgal.py at line 111.

Severity: LOW

Jit Bot commands and options (e.g., ignore issue)
@an1604	Reply...




        aws_secret_access_key='test',
@jit-ci-bandit jit-ci-bandit bot 15 hours ago
Security control: Static Code Analysis Checkmarx

Hardcoded Aws Credentials

AWS credentials are hardcoded in "test", in the file /galgal.py at line 116.

Severity: LOW

Jit Bot commands and options (e.g., ignore issue)
@an1604	Reply...




    )






















# Defining 'pytest_plugins' in a non-top-level conftest is no longer supported:




# It affects the entire test suite instead of just below the conftest as expected.




pytest_plugins = [




    'test_utils.controls.local_output_file_test_setup',




]
