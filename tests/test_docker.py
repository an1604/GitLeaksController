import subprocess
import pytest
import os


def test_docker_image_build():
    """ test if the Docker image builds successfully."""
    image_name = "gitleaks-controller:latest"
    dockerfile_path = os.path.abspath("Dockerfile")

    assert os.path.exists(dockerfile_path), f"Dockerfile not found at {dockerfile_path}"

    build_command = f"docker build -t {image_name} ."
    try:
        result = subprocess.run(
            build_command, shell=True, text=True, capture_output=True, check=True
        )
        assert result.returncode == 0, "Docker build failed"
        print(f"Docker build succeeded. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Docker build failed with error:\n{e.stderr}")


# TODO: test this method at home!
def test_docker_run_gitleaks():
    """ test the `docker run` command for Gitleaks with volume mounting. """
    local_directory = os.path.abspath("test_scan_directory")
    container_directory = "/code/test_directory"
    output_file = "output.json"
    image_name = "gitleaks-controller:latest"

    os.makedirs(local_directory, exist_ok=True)
    mock_file_path = os.path.join(local_directory, "mock_file.txt")
    with open(mock_file_path, "w") as mock_file:
        mock_file.write("This is a test file containing sensitive data.")

    docker_command = (
        f'docker run --rm -v "{local_directory}:{container_directory}" '
        f'{image_name} --dir {container_directory}'
    )
    try:
        result = subprocess.run(
            docker_command, shell=True, text=True, capture_output=True, check=True
        )
        assert result.returncode > 1, f"Docker run failed with error: {result.stderr}"
        expected_output_path = os.path.join(local_directory, output_file)
        assert os.path.exists(expected_output_path), "Output file not found in local directory."
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Docker run failed with error:\n{e.stderr}")
    finally:
        if os.path.exists(local_directory):
            import shutil
            shutil.rmtree(local_directory)
