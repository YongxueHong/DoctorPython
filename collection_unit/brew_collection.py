from misc_unit.utils_misc import convert_to_str
from collections import defaultdict
import re
from platform import machine
import os
from common.shell import doctor_cmd_output,doctor_cmd_status_output
from sys import version_info
from common.error import DoctorError


if version_info.major == 3:
    from urllib.request import urlopen
elif version_info.major == 2:
    from urllib2 import urlopen


class BrewCollection(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.arch = machine()

    def package_info(self, pkg_id, page=1):
        package_dict = defaultdict(list)
        build_num = self.total_num(pkg_id=pkg_id)
        total_pages = (build_num / 50) + 1
        if page <= total_pages:
            package_url = self.base_url + 'packageinfo?buildStart=%d&' \
                                               'packageID=%s&' \
                                               'buildOrder=-completion_time&' \
                                               'tagOrder=name&' \
                                               'tagStart=0#buildlist' \
                               % ((page - 1) * 50, pkg_id)
            # print(package_url)
            html = urlopen(package_url)
            # with urlopen(self.package_url) as html:
            if html.status == 404:
                raise DoctorError('Not found %s : %d'
                                  % (package_url, html.status))
            for item in html.read().splitlines():
                item = convert_to_str(item)
                if re.search(r'<td><a href=\"buildinfo\?buildID=\d+\">.*</a></td>',
                             item):
                    nvr = item.split('>')[2].split('<')[0]
                    build_id= re.search(r'buildID=\d+', item).group().split('=')[-1]
                    package_dict[nvr].append(build_id)
                if re.search(r'<td>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</td>',
                             item):
                    finished_time = item.split('>')[1].split('<')[0]
                    package_dict[nvr].append(finished_time)
        return package_dict

    def build_info(self, build_id):
        # self.id = id
        build_dict = {}
        url = self.base_url + 'buildinfo?buildID=' + build_id

        html = urlopen(url)
        # with urlopen(self.build_url) as html:
        if html.status == 404:
            raise DoctorError('Not found %s : %d'
                              % (url, html.status))
        for item in html.read().splitlines():
            item = convert_to_str(item)
            if '%s.rpm' % self.arch in item:
                rpm_name = re.split(r'\s+', item)[1]
                rpm_url = item.split('\"')[-2]
                build_dict[rpm_name] = rpm_url
        return build_dict

    def download_rpm(self, download_dir, rpm_url, verbose=True):
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        download_cmd = 'cd %s && curl -O %s' % (download_dir, rpm_url)
        output = doctor_cmd_output(cmd=download_cmd, verbose=verbose)
        if verbose:
            return output

    def install_rpm(self, rpms=None, verbose=True):
        if not rpms:
            cmd = 'yum install -y *'
        else:
            cmd = 'yum install -y %s' % rpms
        output = doctor_cmd_output(cmd=cmd, verbose=verbose)
        if verbose:
            return output

    def total_num(self, pkg_url=None, pkg_id=None):
        if pkg_url:
            url = self.base_url + pkg_url
        elif pkg_id:
            url = self.base_url + 'packageinfo?packageID=%s' % pkg_id

        html = urlopen(url)
        # with urlopen(self.pacakage_total_url) as html:
        for item in html.read().splitlines():
            item = convert_to_str(item)
            if pkg_url:
                if re.search(r'Packages \d+ through \d+ of \d+', item):
                    return int(re.findall(r'\d+', item)[-1])
            elif pkg_id:
                if re.search(r'\d+ through \d+ of \d+', item):
                    return int(re.findall(r'\d+', item)[-1])
        return None

    def package_mapping_id(self, pak_name):
        suffix_url = "packages?prefix=%s&order=package_name&inherited=1" % pak_name[0]
        total_pages = self.total_num(pkg_url=suffix_url)

        for page in list(range(0, total_pages, 50)):
            url = self.base_url + 'packages?start=%d&order=package_name&' \
                                  'prefix=%s&inherited=1' % (page, pak_name[0])
            html = urlopen(url)
            # with urlopen(self.package_mapping_url) as html:
            for item in html.read().splitlines():
                item = convert_to_str(item)
                if re.search(r'packageinfo\?packageID=\d+', item):
                    pkg_id = item.split('=')[2].split('\"')[0]
                    name = item.split('>')[2].split('<')[0]
                    if name == pak_name:
                        return pkg_id
        return None

    def search_package_or_build(self, package_name=None, build_name=None, page=1):
        build_num = 0
        package_id = ''
        package_dict = defaultdict(list)
        build_dict = {}
        if package_name:
            suffix_url = 'search?match=glob&type=package&terms=%s' % package_name
        elif build_name:
            suffix_url = 'search?match=glob&type=build&terms=%s' % build_name
        url = self.base_url + suffix_url

        html = urlopen(url)
        for item in html.read().splitlines():
            item = convert_to_str(item)

            if package_name:
                if re.search(r'<th>ID</th><td>\d+</td>', item):
                    package_id = re.findall(r'\d+', item)[0]
                if re.search(r'\d+ through \d+ of \d+', item):
                    build_num =  int(re.findall(r'\d+', item)[-1])
                    # print('build num', build_num)
                    break
            elif build_name:
                if '%s.rpm' % self.arch in item:
                    rpm_name = re.split(r'\s+', item)[1]
                    rpm_url = item.split('\"')[-2]
                    build_dict[rpm_name] = rpm_url
        if build_name:
            return build_dict
        elif package_name:
            total_pages = (build_num / 50) + 1
            # print('total pages', total_pages)
            if page <= total_pages:
                package_url = self.base_url + 'packageinfo?buildStart=%d&' \
                                                   'packageID=%s&' \
                                                   'buildOrder=-completion_time&' \
                                                   'tagOrder=name&' \
                                                   'tagStart=0#buildlist' \
                                   % ((page - 1) * 50, package_id)
                # print(package_url)
                html = urlopen(package_url)
                if html.status == 404:
                    raise DoctorError('Not found %s : %d'
                                      % (package_url, html.status))
                for item in html.read().splitlines():
                    item = convert_to_str(item)
                    if re.search(r'<td><a href=\"buildinfo\?buildID=\d+\">.*</a></td>',
                                 item):
                        nvr = item.split('>')[2].split('<')[0]
                        build_id= re.search(r'buildID=\d+', item).group().split('=')[-1]
                        package_dict[nvr].append(build_id)
                    if re.search(r'<td>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</td>',
                                 item):
                        finished_time = item.split('>')[1].split('<')[0]
                        package_dict[nvr].append(finished_time)
            return package_dict
