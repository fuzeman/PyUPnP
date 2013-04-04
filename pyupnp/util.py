# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  fuzeman <gardiner91@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import urlparse
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


def twisted_absolute_path(path, request):
    """Hack to fix twisted not accepting absolute URIs"""
    parsed = urlparse.urlparse(request.uri)
    if parsed.scheme != '':
        path_parts = parsed.path.lstrip('/').split('/')
        request.prepath = path_parts[0:1]
        request.postpath = path_parts[1:]
        path = request.prepath[0]
    return path, request


def http_parse_raw(data):
    lines = data.split('\r\n')

    version, respCode, respText = None, None, None
    headers = {}

    for x in range(len(lines)):
        if x == 0:
            version, respCode, respText = lines[0].split()
            try:
                respCode = int(respCode)
            except ValueError:
                respCode = respCode
        elif x > 0 and lines[x].strip() != '':
            sep = lines[x].index(':')
            hk = lines[x][:sep].lower()
            hv = lines[x][sep+1:].strip()

            if headers.has_key(hk):
                headers[hk] = [headers[hk], hv]
            else:
                headers[hk] = hv

    return version, respCode, respText, headers


def get_default_address(host):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((host, 80))
        address = s.getsockname()[0]
        s.close()
    except socket.gaierror:
        return None
    return address


def get_default_v4_address():
    return get_default_address("8.8.8.8")


def make_element(name, text):
    elem = et.Element(name)
    elem.text = text
    return elem


def absolute_url(baseUrl, url):
    if url.strip() == '':
        return url

    urlp = urlparse.urlparse(url)
    if urlp.netloc == '':
        url = urlparse.urljoin(baseUrl, url)

    return url


def header_exists(headers, key):
    if not key in headers.keys():
        return False
    return True


def headers_join(headers):
    msg = ""
    for hk, hv in headers.items():
        msg += str(hk) + ': ' + str(hv) + '\r\n'
    return msg


def build_notification_type(uuid, nt):
    if nt == '':
        return 'uuid:' + uuid, 'uuid:' + uuid
    return 'uuid:' + uuid + '::' + nt, nt


def parse_usn(usn):
    usn_split = str(usn).split('::')

    uuid = None
    # Parse UUID
    if len(usn_split) > 0 and usn_split[0].startswith('uuid:'):
        _tmp = usn_split[0].index('uuid:') + 5
        if ':' in usn_split[0][_tmp:]:
            return None
        uuid = usn_split[0][_tmp:]

    schema = None
    name = None
    device_type = None
    version = None
    # Parse URN / upnp:rootdevice
    if len(usn_split) > 1:
        _urn = usn_split[1].split(':')

        # sanity check
        if len(_urn) <= 0:
            return None

        if _urn[0] == 'upnp':
            if len(_urn) != 2:
                return None
            return uuid, True  # [1] = Root?
        elif _urn[0] == 'urn':
            if len(_urn) != 5:
                return None
            schema = _urn[1]
            name = _urn[2].lower()
            device_type = _urn[3]
            version = _urn[4]

            return uuid, False, schema, name, device_type, version  # [1] = Root?

    return uuid,  # [1] = urn type