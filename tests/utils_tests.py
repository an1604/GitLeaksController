import os
import stat
from unittest.mock import MagicMock


def remove_readonly(func, path, _):
    """ clear the read-only attribute and retry """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def mock_process(returncode=0, stderr=""):
    process = MagicMock()
    process.returncode = returncode
    process.stderr = stderr
    return process
