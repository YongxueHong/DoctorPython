import random
import string
from sys import version_info
import os
import subprocess


def py3_to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value


def py3_to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value


def py2_to_unicode(unicode_or_str):
    if isinstance(unicode_or_str, str):
        value = unicode(unicode_or_str, 'utf-8')
    else:
        value = unicode_or_str
    return value


def py2_to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str
    return value


def convert_to_str(bytes_or_unicode):
    if version_info.major == 3:
        return py3_to_str(bytes_or_unicode)
    elif version_info.major == 2:
        return py2_to_str(bytes_or_unicode)


def generate_random_string(length, ignore_str=string.punctuation,
                           convert_str=""):
    """
    Return a random string using alphanumeric characters.
    :param length: Length of the string that will be generated.
    :param ignore_str: Characters that will not include in generated string.
    :param convert_str: Characters that need to be escaped (prepend "\\").
    :return: The generated random string.
    """
    r = random.SystemRandom()
    sr = ""
    chars = string.ascii_letters + string.digits + string.punctuation
    if not ignore_str:
        ignore_str = ""
    for i in ignore_str:
        chars = chars.replace(i, "")

    while length > 0:
        tmp = r.choice(chars)
        if convert_str and (tmp in convert_str):
            tmp = "\\%s" % tmp
        sr += tmp
        length -= 1
    return sr


def py2_get_terminal_size():
    rows, columns = subprocess.check_output(['stty', 'size']).split()
    return int(rows), int(columns)


def py3_get_terminal_size():
    rows = os.get_terminal_size().lines
    columns = os.get_terminal_size().columns
    return rows, columns


if __name__ == '__main__':
    print(version_info.major, type(version_info.major))