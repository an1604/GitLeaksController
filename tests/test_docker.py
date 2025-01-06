import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

import pytest
import os

from git import Repo
import utils_tests as tests_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import controller


def test_run_gitleaks_no_docker_installed():
    """Test the case where Docker is not installed on the user's system."""
    directory_to_scan = "/fake/path"
    output_file = "output_test.json"
    expected_command = f"gitleaks detect --no-git --report-path {directory_to_scan}/output_test.json --source {directory_to_scan}"

    with patch("controller.execute_command") as mock_execute_command, \
            patch("controller.log_error_to_file") as mock_log_error, \
            patch("sys.exit") as mock_exit, \
            patch("os.path.exists", return_value=True):
        mock_execute_command.side_effect = FileNotFoundError("No such file or directory: 'docker'")
        controller.run_gitleaks(directory_to_scan=directory_to_scan, output_file=output_file)

        mock_log_error.assert_called_once_with(
            exit_code=2,
            error_message=(
                f"Failed to execute Gitleaks. Command: {expected_command}. "
                f"Error: No such file or directory: 'docker'"
            )
        )
        mock_exit.assert_called_once_with(2)


def test_docker_image_build():
    """ test if the Docker image builds successfully."""
    image_name = "gitleaks-controller:latest"
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dockerfile_path = os.path.join(project_root, "Dockerfile")

    assert os.path.exists(dockerfile_path), f"Dockerfile not found at {dockerfile_path}"

    build_command = f"docker build -t {image_name} ."
    try:
        os.chdir(project_root)  # Changing the directory to be the same as the Dockerfile
        result = subprocess.run(
            build_command, shell=True, text=True, capture_output=True, check=True, encoding="utf-8"
        )
        assert result.returncode == 0, "Docker build failed"
        print(f"Docker build succeeded. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Docker build failed with error:\n{e.stderr}")


def test_docker_run_gitleaks():
    """ test the `docker run` command for Gitleaks with volume mounting. """
    with tempfile.TemporaryDirectory() as local_directory:
        container_directory = "/code/test_directory"
        output_file = "output_test.json"
        image_name = "gitleaks-controller:latest"
        test_repo_url = "https://github.com/atrull/fake-public-secrets"

        try:
            if os.path.exists(local_directory):
                shutil.rmtree(local_directory, onerror=tests_utils.remove_readonly)
            Repo.clone_from(test_repo_url, local_directory)

            assert os.path.exists(local_directory), "Failed to clone the test repository."

            docker_command = (
                f'docker run --rm -v "{local_directory}:{container_directory}" '
                f'{image_name} --dir {container_directory}'
            )
            result = subprocess.run(
                docker_command, shell=True, text=True, capture_output=True, check=True
            )

            assert result.returncode <= 1, (f"Docker run failed with error: {result.stderr}"
                                            f"\n\nreturncode: {result.returncode}")
            expected_output_path = os.path.join(local_directory, output_file)
            assert os.path.exists(expected_output_path), "Output file not found in local directory."

        except subprocess.CalledProcessError as e:
            pytest.fail(f"Docker run failed with error:\n{e.stderr}")
        finally:
            if os.path.exists(local_directory):
                shutil.rmtree(local_directory, onerror=tests_utils.remove_readonly)
