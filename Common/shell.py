from sys import version_info
import subprocess
from MiscUnit.utils_misc import convert_to_str
import time
from Common.error import DoctorError


def doctor_cmd_output(cmd, timeout=300, verbose=True):
    deadline = time.time() + timeout
    if verbose == True:
        print("Sending command: %s" % cmd)
    if version_info.major == 2:
        sub = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while sub.poll() == None:
            if time.time() > deadline:
                err_info = 'Failed to run \"%s\" under %s sec.' % (cmd, timeout)
                raise DoctorError(err_info)

        try:
            outs, errs = sub.communicate()
        except ValueError:
            pass

        return convert_to_str(outs + errs)

    elif version_info.major == 3:
        sub = subprocess.run(cmd, timeout=timeout, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        return convert_to_str(sub.stdout)


def doctor_cmd_status_output(cmd, timeout=600, verbose=True):
    if verbose == True:
        print("Sending command: %s" % cmd)
    try:
        if version_info.major == 3:
            data = subprocess.check_output(cmd, timeout=timeout, shell=True,
                                           universal_newlines=True,
                                           stderr=subprocess.STDOUT)
        elif version_info.major == 2:
            # No argument timeout in check_output with python2.
            data = subprocess.check_output(cmd, shell=True,
                                           universal_newlines=True,
                                           stderr=subprocess.STDOUT)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data
