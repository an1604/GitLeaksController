import json
import logging
import os
import pdb
import shlex
import subprocess
import argparse
import time

logger = logging.getLogger(__name__)


def redact(str_to_redact, items_to_redact):
    """ return str_to_redact with items redacted
    """
    if items_to_redact:
        for item_to_redact in items_to_redact:
            str_to_redact = str_to_redact.replace(item_to_redact, '***')
    return str_to_redact


def execute_command(command, items_to_redact=None, **kwargs):
    """ execute a command
    """
    command_split = shlex.split(command)
    redacted_command = redact(command, items_to_redact)
    logger.debug(f'executing command: {redacted_command}')
    process = subprocess.run(command_split, capture_output=True, text=True, **kwargs)
    logger.debug(f"executed command: {redacted_command}' returncode: {process.returncode}")
    if process.stdout:
        logger.debug(f'stdout:\n{process.stdout}')
    if process.stderr:
        logger.debug(f'stderr:\n{process.stderr}')
    return process


def run_gitleaks(directory_to_scan, docker_image="zricethezav/gitleaks:latest", output_file="output.json"):
    """Runs Gitleaks using Docker with the specified directory and Docker image.
    """
    if not os.path.exists(directory_to_scan):
        raise FileNotFoundError(f"The directory {directory_to_scan} does not exist.")
    report_path = os.path.join(directory_to_scan, output_file)
    command = (
        f'docker run --rm -v "{directory_to_scan}:/path" '
        f'{docker_image} detect --source=/path --report-path=/path/{output_file}'
    )
    process = execute_command(command)
    if process.returncode == 0:
        logger.info(f"Gitleaks scan completed successfully. Report saved at {report_path}")
    else:
        logger.error(f"Error occurred during Gitleaks scan. Return code: {process.returncode}")
        if process.stderr:
            logger.error(f"Error: {process.stderr}")


def get_findings_from_file(output_filepath):
    """
    parse the original Gitleaks JSON output file and return it.

    :param output_filepath:
    :return: an array of dictionaries
    """
    findings = []
    with open(output_filepath, 'r') as output_file:
        findings = json.load(output_file)

    return findings


def parse_json_output(_current_dir_, output_filename):
    output_filepath = os.path.join(_current_dir_, output_filename)
    custom_output_filepath = os.path.join(_current_dir_, "custom_output.json")

    findings = get_findings_from_file(output_filepath)

    output = {
        'findings': []
    }
    for finding in findings:
        filename = finding['File']
        line_range = f"{finding['StartLine']}-{finding['EndLine']}"
        desc = finding['Description']
        output['findings'].append({
            "filename": filename,
            "line_range": line_range,
            "description": desc
        })

    with open(custom_output_filepath, 'w') as file:
        file.write(json.dumps(output))


if __name__ == '__main__':
    current_dir = os.getcwd()
    target = os.path.join(current_dir, 'fake-public-secrets')
    logger.info(f"Current dir: {target}")

    _process_ = run_gitleaks(target)
    time.sleep(3)

    parse_json_output(target, 'output.json')
