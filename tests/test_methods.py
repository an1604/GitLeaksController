import json
import subprocess

import pytest
from unittest.mock import patch, mock_open, MagicMock

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bonus
import controller


def test_execute_command_success():
    command = "echo Hello, World!"
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=command, returncode=0, stdout="Hello, World!",
                                                            stderr="")
        result = controller.execute_command(command)
        assert result.returncode == 0
        assert result.stdout == "Hello, World!"


def test_execute_command_failure():
    command = "exit 1"
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=command, output="Error")
        with pytest.raises(SystemExit) as excinfo:
            controller.execute_command(command)
        assert excinfo.value.code == 1


def test_gitleaks_on_system():
    """test the case that gitleaks isn't installed on the system."""
    command = "gitleaks detect"
    file_not_found_error = FileNotFoundError("No such file or directory: 'gitleaks'")

    with patch("subprocess.run", side_effect=file_not_found_error), \
            patch("controller.log_error_to_file") as mock_log_error, \
            patch("sys.exit") as mock_exit:
        controller.execute_command(command)

        mock_log_error.assert_called_once_with(
            exit_code=2,
            error_message=(
                f"Executable not found or failed executing the command: {command}. "
                f"Error: {file_not_found_error}"
            )
        )
        mock_exit.assert_called_once_with(2)


def test_run_gitleaks_directory_not_found():
    with pytest.raises(SystemExit) as excinfo:
        controller.run_gitleaks("non_existent_directory", "output_test.json")
    assert excinfo.value.code == 2


def test_parse_json_output_missing_file():
    with pytest.raises(SystemExit) as excinfo:
        controller.parse_json_output("non_existent_directory", "non_existent_file.json")
    assert excinfo.value.code == 2


def test_manipulated_output():
    """ tests the manipulated output using the method parse_json_output"""
    real_output_filename = "output_test.json"
    manipulated_output_filename = "custom_output_test.json"
    tests_dirpath = os.path.join(os.getcwd(), 'tests')
    real_output_filepath = os.path.join(tests_dirpath, real_output_filename)
    manipulated_output_filepath = os.path.join(tests_dirpath, manipulated_output_filename)

    # Step 1: Ensure the test files exist
    assert os.path.exists(real_output_filepath), f"Test file not found: {real_output_filepath}"
    assert os.path.exists(manipulated_output_filepath), f"Test file not found: {manipulated_output_filepath}"
    # Step 2: Load real output and compare with `get_findings_from_output_file`
    real_output = controller.get_findings_from_output_file(real_output_filepath)
    with open(real_output_filepath, 'r') as real_output_file:
        expected_real_output = json.load(real_output_file)
    assert real_output == expected_real_output, "Mismatch between real output and expected real output."
    # Step 3: Generate manipulated output using `parse_json_output`
    manipulated_output = controller.parse_json_output(
        _current_dir_=tests_dirpath,
        __output_filename__=real_output_filename
    )
    # Step 4: Compare manipulated output with expected manipulated output
    with open(manipulated_output_filepath, 'r') as manipulated_output_file:
        expected_manipulated_output = json.load(manipulated_output_file)
    assert manipulated_output == expected_manipulated_output, "Mismatch between manipulated output and expected manipulated output."


def test_get_findings_from_output_file_json_decode_error():
    """Test the case where the JSON file has invalid content."""
    invalid_json_content = "{ invalid json }"  # Simulating a broken JSON file
    mock_filepath = "/fake/path/output.json"

    with patch("builtins.open", mock_open(read_data=invalid_json_content)), \
            patch("controller.log_error_to_file") as mock_log_error, \
            patch("sys.exit") as mock_exit:
        controller.get_findings_from_output_file(mock_filepath)

        mock_log_error.assert_called_once()
        args, kwargs = mock_log_error.call_args
        assert kwargs['exit_code'] == 3
        assert "JSON decoding error" in kwargs['error_message']
        mock_exit.assert_called_once_with(3)


def test_get_parser_defaults():
    parser = controller.get_parser()
    args = parser.parse_args([])

    assert args.dirname == os.getcwd()
    assert args.output_filename == "output_test.json"
    assert args.show_result is True
    assert args.bonus is True


def test_get_parser_custom_args():
    parser = controller.get_parser()
    args = parser.parse_args([
        '--dir', '/custom/directory',
        '--output_filename', 'custom_output.json',
        '--no-show_result',
        '--no-bonus'
    ])

    assert args.dirname == '/custom/directory'
    assert args.output_filename == 'custom_output.json'
    assert args.show_result is False
    assert args.bonus is False


def test_get_parser_invalid_args():
    parser = controller.get_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--invalid-arg"])
    assert excinfo.value.code == 2


def test_show_results_with_bonus():
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


def test_main_success():
    mock_args = MagicMock()
    mock_args.dirname = "/fake/dir"
    mock_args.output_filename = "output.json"
    mock_args.show_result = True
    mock_args.bonus = True

    with patch("controller.run_gitleaks") as mock_run_gitleaks, \
            patch("controller.parse_json_output") as mock_parse_json_output, \
            patch("controller.show_results") as mock_show_results:
        mock_run_gitleaks.return_value = MagicMock(returncode=0)
        mock_parse_json_output.return_value = {"findings": []}

        controller.main(mock_args)

        mock_run_gitleaks.assert_called_once_with("/fake/dir", "output.json")
        mock_parse_json_output.assert_called_once_with("/fake/dir", "output.json")
        mock_show_results.assert_called_once_with({"findings": []}, bonus=True)


def test_main_clean_outputfile_exception():
    mock_args = MagicMock()
    mock_args.dirname = "/fake/dir"
    mock_args.output_filename = "output.json"

    with patch("controller.clean_outputfile", side_effect=Exception("Clean error")), \
            patch("controller.log_error_to_file") as mock_log_error, \
            patch("sys.exit") as mock_exit:
        controller.main(mock_args)

        mock_log_error.assert_called_once_with(exit_code=2, error_message="Clean error")
        mock_exit.assert_called_once_with(2)
