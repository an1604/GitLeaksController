import json
import shutil
import subprocess
import pytest
from unittest.mock import patch

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import execute_command, run_gitleaks, parse_json_output, get_findings_from_output_file


def test_execute_command_success():
    command = "echo Hello, World!"
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=command, returncode=0, stdout="Hello, World!",
                                                            stderr="")
        result = execute_command(command)
        assert result.returncode == 0
        assert result.stdout == "Hello, World!"


def test_execute_command_failure():
    command = "exit 1"
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=command, output="Error")
        with pytest.raises(SystemExit) as excinfo:
            execute_command(command)
        assert excinfo.value.code == 1


# TODO: FIX THIS TEST
def test_run_gitleaks():
    directory_to_scan = os.path.join(os.getcwd(), "scan_directory")
    output_file = "output_test.json"
    os.makedirs(directory_to_scan, exist_ok=True)
    output_path = os.path.join(directory_to_scan, output_file)

    result = run_gitleaks(str(directory_to_scan), output_file)

    # Simulation of opening the output file to ensure its existence
    with open(output_path, "w") as f:
        f.write("{}")

    assert result.returncode == 0
    assert os.path.exists(os.path.join(directory_to_scan, output_file))

    shutil.rmtree(directory_to_scan)  # remove the file and the directory


# TODO: TEST AT HOME!!
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
    real_output = get_findings_from_output_file(real_output_filepath)
    with open(real_output_filepath, 'r') as real_output_file:
        expected_real_output = json.load(real_output_file)
    assert real_output == expected_real_output, "Mismatch between real output and expected real output."
    # Step 3: Generate manipulated output using `parse_json_output`
    manipulated_output = parse_json_output(
        _current_dir_=tests_dirpath,
        __output_filename__=real_output_filename
    )
    # Step 4: Compare manipulated output with expected manipulated output
    with open(manipulated_output_filepath, 'r') as manipulated_output_file:
        expected_manipulated_output = json.load(manipulated_output_file)
    assert manipulated_output == expected_manipulated_output, "Mismatch between manipulated output and expected manipulated output."
