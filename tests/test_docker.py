import json
import shutil
import subprocess
import sys
import tempfile

import pytest
import os

from git import Repo
import stat

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import parse_json_output, get_findings_from_output_file


def remove_readonly(func, path, _):
    """ clear the read-only attribute and retry """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def check_matching_files(local_directory, output_file):
    """ checks the output from the Gitleaks' scan """
    # Step 1: check the existence of the original output file and if its match the output of the function
    real_output_filepath = os.path.join(local_directory, output_file)
    real_output = get_findings_from_output_file(real_output_filepath)
    with open(real_output_filepath, 'r') as real_output_file:
        expected_real_output = json.load(real_output_file)
    assert real_output == expected_real_output, "Mismatch between real output and expected real output."

    # Step 2: check the manipulated JSON file from the scan
    custom_output_test_filename = "custom_output_test.json"
    manipulated_output_filepath = os.path.join(local_directory, custom_output_test_filename)
    manipulated_output = parse_json_output(
        _current_dir_=local_directory,
        __output_filename__=output_file
    )
    with open(manipulated_output_filepath, 'r') as manipulated_output_file:
        expected_manipulated_output = json.load(manipulated_output_file)

    assert manipulated_output == expected_manipulated_output, "Mismatch between manipulated output and expected manipulated output."


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
                shutil.rmtree(local_directory, onerror=remove_readonly)
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
                shutil.rmtree(local_directory, onerror=remove_readonly)
