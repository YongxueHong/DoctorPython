from MiscUnit.utils_misc import convert_to_str
from collections import defaultdict
import re
from platform import machine
import os
from Common.shell import doctor_cmd_output,doctor_cmd_status_output
from sys import version_info


if version_info.major == 3:
    from urllib.request import urlopen
elif version_info.major == 2:
    from urllib2 import urlopen


class Brew(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.arch = machine()

    def package_info(self, id):
        self.package_dict = defaultdict(list)
        self.id = id
        self.package_url = self.base_url + 'packageinfo?packageID=' + self.id

        html = urlopen(self.package_url)
        for item in html.read().splitlines():
            item = convert_to_str(item)
            if re.search(r'<td><a href=\"buildinfo\?buildID=\d+\">.*</a></td>',
                         item):
                nvr = item.split('>')[2].split('<')[0]
                build_id= re.search(r'buildID=\d+', item).group().split('=')[-1]
                self.package_dict[nvr].append(build_id)
            if re.search(r'<td>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</td>',
                         item):
                finished_time = item.split('>')[1].split('<')[0]
                self.package_dict[nvr].append(finished_time)
        return self.package_dict

    def build_info(self, id):
        self.id = id
        self.build_dict = {}
        self.build_url = self.base_url + 'buildinfo?buildID=' + self.id

        html = urlopen(self.build_url)
        for item in html.read().splitlines():
            item = convert_to_str(item)
            if '%s.rpm' % self.arch in item:
                rpm_name = re.split(r'\s+', item)[1]
                rpm_url = item.split('\"')[-2]
                self.build_dict[rpm_name] = rpm_url
        return self.build_dict

    def rpm_download(self, download_dir, rpm_url, verbose=True):
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        download_cmd = 'cd %s && curl -O %s' % (download_dir, rpm_url)
        output = doctor_cmd_output(cmd=download_cmd, verbose=verbose)
        if verbose:
            print(output)
