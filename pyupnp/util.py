import socket
import urlparse
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


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
    except socket.gaierror, e:
        return None
    return address


def get_default_v4_address():
    return get_default_address("8.8.8.8")


def make_element(name, text):
    elem = et.Element(name)
    elem.text = text
    return elem


def get_default_v6_address():
    # TODO: Fix so this works when internet is inaccessible
    return get_default_address("ipv6.google.com")


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