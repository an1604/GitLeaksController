import json
import subprocess

import pytest
from unittest.mock import patch

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bonus import LeakReport
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


def test_show_results_with_bonus():
    tests_dirpath = os.path.join(os.getcwd(), 'tests')
    real_output_filename = 'output_test.json'

    custom_output = controller.parse_json_output(tests_dirpath, real_output_filename)
    expected_output = [LeakReport(**finding_dict) for finding_dict in custom_output['findings']]

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
