import json
import logging
import os
import pdb
import shlex
import subprocess
import argparse

from bonus import LeakReport

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


def run_gitleaks(directory_to_scan, output_file="output.json"):
    """Runs Gitleaks Locally/Docker with the specified directory and Docker image.
    """
    if not os.path.exists(directory_to_scan):
        raise FileNotFoundError(f"The directory {directory_to_scan} does not exist.")
    report_path = os.path.join(directory_to_scan, output_file)

    command = f"gitleaks detect --no-git --report-path {directory_to_scan}/output.json --source {directory_to_scan} "
    process = execute_command(command)
    if process.returncode == 0:
        logger.info(f"Gitleaks scan completed successfully. No leaks found. Report saved at {report_path}")
    elif process.returncode == 1:
        logger.warning(f"Gitleaks scan completed. Leaks detected. Report saved at {report_path}")
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
    try:
        findings = []
        with open(output_filepath, 'r') as output_file:
            findings = json.load(output_file)

        return findings['findings']
    except:
        return findings


def parse_json_output(_current_dir_, __output_filename__):
    output_filepath = os.path.join(_current_dir_, __output_filename__)
    __custom_output_filepath__ = os.path.join(_current_dir_, "custom_output.json")

    findings = get_findings_from_file(output_filepath)

    output = {
        'findings': []
    }
    for __finding__ in findings:
        filename = __finding__['File']
        line_range = f"{__finding__['StartLine']}-{__finding__['EndLine']}"
        desc = __finding__['Description']
        finding_dict = {
            "filename": filename,
            "line_range": line_range,
            "description": desc
        }
        output['findings'].append(finding_dict)
    return output


def get_parser():
    """
    Returns an argument parser for the gitleaks wrapper script.

    The script scans a given directory for leaks using gitleaks
    and outputs results to a specified JSON file.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description='A Python script that wraps the gitleaks tool to scan a given directory for leaks.'
    )
    default_dir = os.getcwd()

    parser.add_argument(
        '--dir',
        dest='dirname',
        type=str,
        default=default_dir,
        help=f"Path to the directory to scan. Default: {default_dir}"
    )

    parser.add_argument(
        '--output_filename',
        dest='output_filename',
        type=str,
        default="output.json",
        help="Output filename for scan results. Default: 'output.json'"
    )

    parser.add_argument(
        '--show_result',
        dest='show_result',
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Printing output directly to the terminal. Default: True"
    )

    parser.add_argument(
        '--bonus',
        dest='bonus',
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include the bonus section. Default: True"
    )

    return parser


def show_results(custom_output, bonus):
    if bonus:
        custom_output = [LeakReport(**finding_dict) for finding_dict in custom_output['findings']]
        print("Here are all the pydantic models:")
        for i, finding in enumerate(custom_output):
            print(f"{i + 1}) {finding}")
    else:
        print("Here are all the JSON objects:")
        print(custom_output)


def main(__args__):
    dirname = __args__.dirname
    output_filename = __args__.output_filename

    _process_ = run_gitleaks(dirname, output_filename)

    custom_output = parse_json_output(dirname, output_filename)
    if __args__.show_result:
        print(f"__args__.bonus = {__args__.bonus}")
        show_results(custom_output, bonus=__args__.bonus)


if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)
