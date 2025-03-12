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
        aws_secret_access_key='test',
    )


# Defining 'pytest_plugins' in a non-top-level conftest is no longer supported:
# It affects the entire test suite instead of just below the conftest as expected.
pytest_plugins = [
    'test_utils.controls.local_output_file_test_setup',
]
