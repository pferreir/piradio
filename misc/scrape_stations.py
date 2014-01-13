import datetime
import sys
import re
import requests
import configparser

from lxml import etree
from bs4 import BeautifulSoup
import yaml


HEADERS = {
    'user-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)'
}

PROTOCOLS = ('http', 'mms', 'rtsp')


class ParsingError(Exception):
    pass


class MalformedPlaylistError(Exception):
    def __init__(self, msg):
        self.msg = msg

def error(text):
    sys.stderr.write(text + '\n')


def _parse_m3u(text):
    lines = list(l.strip() for l in text.splitlines(True))
    for l in lines:
        if not l or l.startswith('#'):
            continue
        if l.startswith(PROTOCOLS):
            return l

    raise ParsingError()


def _parse_pls(text):
    config = configparser.ConfigParser()
    try:
        config.read_string(text)
        file1 = config['playlist'].get('File1')
        if not file1:
            raise MalformedPlaylistError("No File1 entry")
        return file1
    except configparser.ParsingError:
        raise ParsingError


def _parse_asx(text):
    parser = etree.XMLParser(ns_clean=True, recover=True)
    el = etree.fromstring(text.lower(), parser)

    refs = el.find('entry/ref')

    if refs is None:
        refs = el.find('repeat/entry/ref')

    return refs.attrib['href']


def _parse_wpl(text):
    parser = etree.XMLParser(ns_clean=True, recover=True)
    el = etree.fromstring(text.lower(), parser)
    return el.find('body/seq/media').attrib['src']


def _parse_adv_asx(text):
    config = configparser.ConfigParser()

    try:
        config.read_string(text)
        return config['Reference']['Ref1'].strip()
    except configparser.ParsingError:
        raise ParsingError


def _decode(text):
    try:
        return text.decode('utf-8')
    except UnicodeDecodeError:
        return text.decode('latin1')


def get_url(url, text, ctype):
    # re.findall(r'((?:https?|mms|rtsp)://[^\s"\']*)(?:\'|"|$|\s)', text)

    if ctype == 'application/vnd.ms-wpl':
        return _parse_wpl(text)
    elif ctype.startswith(('audio/x-scpls', 'application/pls+xml')):
        return _parse_pls(text)
    elif ctype.startswith(('video/x-ms-asf', 'video/x-ms-asx')):
        if text.lower().startswith('<asx'):
            return _parse_asx(text)
        elif text.startswith('[Reference]'):
            return _parse_adv_asx(text)
    elif ctype == 'audio/x-mpegurl':
        return _parse_m3u(text)
    else:
        error('UNKNOWN: {} ({})'.format(ctype, url))
    return None


def process_radio(name, playlist_url):
    if playlist_url.startswith('http'):
        try:
            r = requests.get(playlist_url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                url = get_url(playlist_url, _decode(r.content), r.headers['content-type'])
                if url:
                    return url
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            error("CONNECTION PROBLEM: {} ({})".format(name, playlist_url))
        except ParsingError:
            error("PARSE ERROR: {} ({})".format(name, playlist_url))
        except MalformedPlaylistError as e:
            error("MALFORMED PLAYLIST ERROR: {} ({} {})".format(e.msg, name, playlist_url))
    else:
        if playlist_url.startswith(PROTOCOLS):
            return playlist_url
        else:
            error("URL PROTOCOL NOT SUPPORTED: {} ({})".format(playlist_url, name))
    return None


if __name__ == '__main__':
    r = requests.get(sys.argv[1], headers=HEADERS)
    soup = BeautifulSoup(r.content)

    stations = {}

    for entry in soup.find_all('tr')[1:]:
        tags = entry.find_all('td')
        name = tags[0].text.strip()

        url = process_radio(name, tags[3].a['href'])

        if url:
            stations[name] = {
                'url': url
            }

    sys.stdout.write(
    """# Radio station list
# generated from {} on {}
""".format(sys.argv[1], datetime.datetime.now()))
    sys.stdout.write(yaml.dump(stations))
