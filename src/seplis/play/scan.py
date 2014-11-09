import os, os.path
import re
import logging
from seplis import config
from seplis.play import constants

SCAN_TYPES = (
    'shows',
)

class Episode(object):

    def __init__(self, show_id, number, last_changed, path, metadata):
        self.show_id = show_id
        self.number = number
        self.last_changed = last_changed
        self.path = path
        self.metadata = metadata

class Parsed_episode_season(object):

    def __init__(self, show_title, season, episode, path):
        self.show_title = show_title
        self.season = season
        self.episode = episode
        self.path = path

class Parsed_episode_airdate(object):

    def __init__(self, show_title, airdate, path):
        self.show_title = show_title
        self.airdate = airdate
        self.path = path

class Parsed_episode_number(object):

    def __init__(self, show_title, number, path):
        self.show_title = show_title
        self.number = number
        self.path = path

class Play_scan(object):

    def __init__(self, scan_path, type_='shows'):
        if not scan_path:
            raise Exception('scan_path is missing')
        if not os.path.exists(scan_path):
            raise Exception('scan_path "{}" does not exist'.format(scan_path))
        if type_ not in SCAN_TYPES:
            raise Exception('scan type: "{}" is not supported'.format(type_))
        self.scan_path = scan_path
        self.type = type_

    def scan(self):
        pass

    def get_files(self):
        files = []
        for dirname, dirnames, filenames in os.walk(self.scan_path):
            for file_ in filenames:
                info = os.path.splitext(file_)
                if len(info) != 2:
                    continue

                if info[1][1:] not in config['play']['media_types']:
                    continue
                files.append(
                    os.path.join(dirname, file_)
                )
        return files

def parse_episodes(files):
    episodes = []
    for file_ in files:
        e = parse_episode(file_)
        if e:
            episodes.append(e)
    return episodes

def parse_episode(file_):
    for pattern in constants.FILENAME_PATTERNS:
        try:
            match = re.match(
                pattern, 
                os.path.basename(file_), 
                re.VERBOSE
            )
            if not match:
                continue
            return _parse_episode_info_from_file(
                file_=file_, 
                match=match,
            )
        except re.error as error:
            logging.exception('episode parse re error: {}'.format(error))
        except:
            logging.exception('episode parse pattern: {}'.format(pattern))


def _parse_episode_info_from_file(file_, match):
    fields = match.groupdict().keys()
    season = None
    if 'show_title' not in fields:
        return None
    show_title = match.group('show_title').strip()

    season = None
    if 'season' in fields:
        season = int(match.group('season'))

    number = None
    if 'number' in fields:
        number = match.group('number')
    elif 'number1' in fields:
        number = match.group('number1')
    elif 'numberstart' in fields:
        number = match.group('numberstart')
    if number:
        number = int(number)

    date = None
    if 'year' in fields and 'month' in fields and 'day' in fields:
        airdate = '{}-{}-{}'.format(
            match.group('year'),
            match.group('month'),
            match.group('day'),
        )

    if season and number:
        return Parsed_episode_season(
            show_title=show_title,
            season=season,
            episode=number,
            path=file_,
        )
    elif not season and number:
        return Parsed_episode_number(
            show_title=show_title,
            number=number,
            path=file_,
        )
    elif airdate:
        return Parsed_episode_airdate(
            show_title=show_title,
            airdate=airdate,
            path=file_,
        )

def main():
    pass