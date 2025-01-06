import sys
from unittest.mock import patch

import os

import pytest

import utils_tests as tests_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import controller


def test_run_gitleaks_directory_not_found():
    """trying to pass an invalid directory to run_gitleaks() to see the result"""
    with pytest.raises(SystemExit) as excinfo:
        controller.run_gitleaks("non_existent_directory", "output_test.json")
    assert excinfo.value.code == 2


def test_run_gitleaks_no_leaks():
    directory_to_scan = "/test/path"
    output_file = "output_test.json"
    expected_report_path = os.path.join(directory_to_scan, output_file)

    with patch("controller.os.path.exists", return_value=True), \
            patch("controller.execute_command", return_value=tests_utils.mock_process(returncode=0)), \
            patch("controller.logger.info") as mock_logger_info:
        result = controller.run_gitleaks(directory_to_scan, output_file)

        assert result.returncode == 0
        mock_logger_info.assert_called_once_with(
            f"Gitleaks scan completed successfully. No leaks found. Report saved at {expected_report_path}"
        )


def test_run_gitleaks_with_leaks():
    directory_to_scan = "/test/path"
    output_file = "output_test.json"
    expected_report_path = os.path.join(directory_to_scan, output_file)

    with patch("controller.os.path.exists", return_value=True), \
            patch("controller.execute_command", return_value=tests_utils.mock_process(returncode=1)), \
            patch("controller.logger.warning") as mock_logger_warning:
        result = controller.run_gitleaks(directory_to_scan, output_file)

        assert result.returncode == 1
        mock_logger_warning.assert_called_once_with(
            f"Gitleaks scan completed. Leaks detected. Report saved at {expected_report_path}"
        )


def test_run_gitleaks_execution_error():
    directory_to_scan = "/test/path"
    output_file = "output_test.json"

    with patch("controller.os.path.exists", return_value=True), \
            patch("controller.execute_command",
                  return_value=tests_utils.mock_process(returncode=2, stderr="General error")), \
            patch("controller.logger.error") as mock_logger_error, \
            patch("controller.log_error_to_file") as mock_log_error:
        controller.run_gitleaks(directory_to_scan, output_file)

        mock_logger_error.assert_any_call("Error occurred during Gitleaks scan. Return code: 2")
        mock_logger_error.assert_any_call("Error: General error")
        mock_log_error.assert_called_once_with(
            exit_code=2,
            error_message="General error"
        )
