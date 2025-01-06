import shutil
import subprocess
import tempfile

import pytest
import os

from git import Repo
import utils_tests as tests_utils


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
