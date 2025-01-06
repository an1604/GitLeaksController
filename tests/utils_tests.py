import os
import stat


def remove_readonly(func, path, _):
    """ clear the read-only attribute and retry """
    os.chmod(path, stat.S_IWRITE)
    func(path)
