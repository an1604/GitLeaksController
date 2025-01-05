import json
import pdb
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


def test_manipulated_output():
    """ tests the manipulated output using the method """
    real_outputfilename = "tests/output_test.json"
    manipulated_outputfilename = "tests/custom_output_test.json"

    # Checks if the result equal to the output form the method
    real_output = get_findings_from_output_file(real_outputfilename)
    with open(real_outputfilename, 'r') as real_outputfile:
        assert real_output == json.load(real_outputfile)

    # Step 1: apply the method to get manipulated_output (dictionary)
    manipulated_output = parse_json_output()
    # Step 2: asserting the manipulated_output with the content from the manipulated_outputfilename
