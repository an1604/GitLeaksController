import json

import pytest
from unittest.mock import patch, mock_open, MagicMock

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bonus
import controller


def test_show_results_with_bonus():
    """tests the cases where we want to print the results to the console with the bonus
    flag set to true (i.e., see the pydantic models)
    """
    tests_dirpath = os.path.join(os.getcwd(), 'tests')
    real_output_filename = 'output_test.json'

    custom_output = controller.parse_json_output(tests_dirpath, real_output_filename)
    expected_output = [bonus.LeakReport(**finding_dict) for finding_dict in custom_output['findings']]

    with patch('builtins.print') as mock_print:
        controller.show_results(custom_output, bonus=True)
        mock_print.assert_any_call("\nHere are all the pydantic models:")

        # Verify each expected output is printed correctly
        for i, expected_item in enumerate(expected_output, start=1):
            formatted_output = f"{i}) {expected_item}"  # Format to match the expected print
            mock_print.assert_any_call(formatted_output)


def test_show_results_without_bonus():
    """tests the cases where we want to print the results to the console with
    the bonus flag set to false (i.e., see the result as the manipulated JSON)"""
    custom_output = {
        'findings': [{'filename': 'test.py', 'line_range': '1-2', 'description': 'Sensitive info'}]
    }
    with patch('builtins.print') as mock_print:
        controller.show_results(custom_output, bonus=False)

        mock_print.assert_any_call("\nHere are all the JSON objects:")
        mock_print.assert_any_call("1) {'filename': 'test.py', 'line_range': '1-2', 'description': 'Sensitive info'}")


def test_log_error_to_file_success():
    """ test that the error is logged correctly to a JSON file. """
    exit_code = 1
    error_message = "This is a test error"
    error_file = "test_error.json"

    try:
        bonus.log_error_to_file(exit_code, error_message, error_file)
        with open(error_file, "r") as f:
            error_data = json.load(f)

        expected_data = {
            "exit_code": exit_code,
            "error_message": error_message
        }
        assert error_data == expected_data, "Error data in file does not match expected data."
    finally:
        if os.path.exists(error_file):
            os.remove(error_file)


def test_log_error_to_file_with_mocking():
    """ test the method using mocking to avoid the actual file writes """
    exit_code = 2
    error_message = "Another test error"
    error_file = "mock_error.json"

    expected_data = json.dumps({
        "exit_code": exit_code,
        "error_message": error_message
    }, indent=4)

    with patch("builtins.open", mock_open()) as mock_file, patch("builtins.print") as mock_print:
        bonus.log_error_to_file(exit_code, error_message, error_file)

        # Step 1: Verify the file write content
        mock_file.assert_called_once_with(error_file, "w")
        mock_file().write.assert_called()
        written_data = "".join(call[0][0] for call in mock_file().write.call_args_list)
        assert written_data == expected_data, "Written data does not match the expected JSON structure."

        # Step 2: Verify the printed messages
        mock_print.assert_any_call(f"Error logged to {error_file}")
        mock_print.assert_any_call({
            "exit_code": exit_code,
            "error_message": error_message
        })
