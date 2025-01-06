import json
import logging
import os
import pdb
import shlex
import stat
import subprocess
import argparse
import sys

from bonus import LeakReport, log_error_to_file

# Configure logging
LOG_FILE = "runtime_logs.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="w")
    ]
)
logger = logging.getLogger(__name__)


class MyCustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser to handle unrecognized arguments."""

    def error(self, message):
        error_message = f"Gitleaks scan failed: {message}"
        log_error_to_file(exit_code=2, error_message=error_message)
        sys.exit(2)


def execute_command(command, **kwargs):
    """ execute a Gitleaks command in a subprocess """
    try:
        command_split = shlex.split(command)
        process = subprocess.run(command_split, capture_output=True, text=True, **kwargs)
        if process.stdout:
            logger.debug(f'stdout:\n{process.stdout}')
        if process.stderr:
            logger.debug(f'stderr:\n{process.stderr}')
        return process
    except subprocess.CalledProcessError as e:
        log_error_to_file(exit_code=e.returncode, error_message=str(e))
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        log_error_to_file(exit_code=2,
                          error_message=f"Executable not found or failed executing the command: {command}. Error: {str(e)}"
                          )
        sys.exit(2)


def run_gitleaks(directory_to_scan, output_file):
    if not os.path.exists(directory_to_scan):
        error_message = f"The directory {directory_to_scan} does not exist."
        log_error_to_file(exit_code=2, error_message=error_message)
        sys.exit(2)

    report_path = os.path.join(directory_to_scan, output_file)
    command = f"gitleaks detect --no-git --report-path {directory_to_scan}/output_test.json --source {directory_to_scan}"
    try:
        process = execute_command(command)
        if process is not None:
            if process.returncode == 0:
                logger.info(f"Gitleaks scan completed successfully. No leaks found. Report saved at {report_path}")
            elif process.returncode == 1:
                logger.warning(f"Gitleaks scan completed. Leaks detected. Report saved at {report_path}")
            else:
                logger.error(f"Error occurred during Gitleaks scan. Return code: {process.returncode}")
                if process.stderr:
                    logger.error(f"Error: {process.stderr}")
                    log_error_to_file(exit_code=process.returncode, error_message=process.stderr)
        return process
    except FileNotFoundError as e:
        log_error_to_file(
            exit_code=2,
            error_message=f"Failed to execute Gitleaks. Command: {command}. Error: {str(e)}"
        )
        sys.exit(2)


def get_findings_from_output_file(output_filepath):
    """ parse the original Gitleaks JSON output file and return it """
    try:
        findings = []
        with open(output_filepath, 'r') as output_file:
            findings = json.load(output_file)
        return findings
    except FileNotFoundError:
        log_error_to_file(exit_code=2, error_message=f"File not found: {output_filepath}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        log_error_to_file(exit_code=3, error_message=f"JSON decoding error: {str(e)}")
        sys.exit(3)


def parse_json_output(_current_dir_, __output_filename__,
                      save_customize_output=True):
    """ given the output JSON file, this method manipulates the output as requested in the assignment """
    output_filepath = os.path.join(_current_dir_, __output_filename__)
    findings = get_findings_from_output_file(output_filepath)

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
    if save_customize_output:  # by default, the custom output is saved inside the container
        __custom_output_filepath__ = os.path.join(_current_dir_, "custom_output_test.json")
        with open(__custom_output_filepath__, 'w') as f:
            json.dump(output, f, indent=4)

    return output


def get_parser():
    """ returns an argument parser for the gitleaks wrapper script """
    parser = MyCustomArgumentParser(
        description='A Python script that wraps the Gitleaks tool to scan a given directory for leaks.'
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
        default="output_test.json",
        help="Output filename for scan results. Default: 'output_test.json'"
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
    if bonus:  # converting the JSONs into pydantic objects of the bonus flag is on
        custom_output = [LeakReport(**finding_dict) for finding_dict in custom_output['findings']]
        print("\nHere are all the pydantic models:")
    else:
        custom_output = custom_output['findings']
        print("\nHere are all the JSON objects:")

    for i, finding in enumerate(custom_output):
        print(f"{i + 1}) {finding}")


def clean_outputfile(output_filename):
    try:
        with open(output_filename, 'w') as file:
            file.write('')
        print(f"Successfully cleaned the output file: {output_filename}")
    except Exception as e:
        error_message = f"Failed to clean the output file: {output_filename}. Error: {str(e)}"
        log_error_to_file(exit_code=2, error_message=error_message)


def main(__args__):
    try:
        dirname = __args__.dirname
        output_filename = __args__.output_filename

        clean_outputfile(os.path.join(dirname, output_filename))

        _process_ = run_gitleaks(dirname, output_filename)

        custom_output = parse_json_output(dirname,
                                          output_filename)  # will hold the manipulated output in the different format
        if __args__.show_result:
            show_results(custom_output, bonus=__args__.bonus)
    except Exception as e:
        log_error_to_file(exit_code=2, error_message=str(e))
        sys.exit(2)


if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)
