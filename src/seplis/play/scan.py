import os, os.path, logging, subprocess
from datetime import datetime
from seplis import config, Client, utils
from seplis.play import models
from seplis.play.decorators import new_session
from guessit import guessit


def scan():
    if not config.data.play.scan:
        raise Exception('''
            Nothing to scan. Add a path in the config file.

            Example:

                play:
                    scan:
                        -
                            type: series
                            path: /a/path/to/the/series
            ''')
    for s in config.data.play.scan:    
        try:
            scanner = None
            if s.type == 'series':
                scanner = Series_scan(s.path)
            elif s.type == 'movies':
                scanner = Movie_scan(s.path)
            if not scanner:
                raise Exception(f'Scan type: "{s.type}" is not supported')
            scanner.scan()
        except:        
            logging.exception('play scan')

def cleanup():
    logging.info('Cleanup started')
    cleanup_episodes()
    cleanup_movies()

def cleanup_episodes():
    with new_session() as session:
        episodes = session.query(models.Episode).all()
        deleted_count = 0
        for e in episodes:
            if os.path.exists(e.path):
                continue
            deleted_count += 1
            session.delete(e)
        session.commit()
        logging.info(f'{deleted_count} episodes was deleted from the database')

def cleanup_movies():
    with new_session() as session:
        movies = session.query(models.Movie).all()
        deleted_count = 0
        for m in movies:
            if os.path.exists(m.path):
                continue
            deleted_count += 1
            session.delete(m)
        session.commit()
        logging.info(f'{deleted_count} movies was deleted from the database')

class Play_scan(object):

    def __init__(self, scan_path, type_):
        if not os.path.exists(scan_path):
            raise Exception(f'scan_path "{scan_path}" does not exist')
        self.scan_path = scan_path
        self.type = type_
        self.client = Client(url=config.data.client.api_url)

    def save_item(self, item, path):
        raise NotImplementedError()

    def parse(self, filename):
        raise NotImplementedError()

    def delete_item(self, item, path):
        raise NotImplementedError()

    def get_files(self):
        '''
        Looks for files in the `self.scan_path` directory.
        '''
        files = []
        for dirname, dirnames, filenames in os.walk(self.scan_path):
            for file_ in filenames:
                info = os.path.splitext(file_)
                if file_.startswith('._'):
                    continue
                if len(info) != 2:
                    continue
                if info[1][1:].lower() not in config.data.play.media_types:
                    continue
                files.append(
                    os.path.join(dirname, file_)
                )
        return files

    def get_metadata(self, path):
        '''
        :returns: dict
            metadata is a `dict` taken from the result of ffprobe.
        '''
        logging.info(f'Retrieving metadata from "{path}"')
        if not os.path.exists(path):
            raise Exception(f'Path "{path}" does not exist')
        ffprobe = os.path.join(config.data.play.ffmpeg_folder, 'ffprobe')
        if not os.path.exists(ffprobe):
            raise Exception(f'ffprobe not found in "{config.data.play.ffmpeg_folder}"')
        cmd = [
            ffprobe,
            '-show_streams',
            '-show_format',
            '-loglevel', 'quiet',
            '-print_format', 'json',
            path,
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        data = process.stdout.read()
        error = process.stderr.read()
        if error:        
            if isinstance(error, bytes):
                error = error.decode('utf-8')   
            raise Exception('FFprobe error: {}'.format(error))
        if not data:
            return
        if isinstance(data, bytes):
            data = data.decode('utf-8')        
        logging.info(f'Metadata retrieved from "{path}"')
        data = utils.json_loads(data)
        return data

    def get_file_modified_time(self, path):
        return datetime.utcfromtimestamp(
            os.path.getmtime(path)
        )

class Movie_scan(Play_scan):

    def __init__(self, scan_path):
        super().__init__(
            scan_path=scan_path,
            type_='movies',
        )

    def scan(self):
        logging.info(f'Scanning: {self.scan_path}')
        files = self.get_files()
        for f in files:
            title = self.parse(f)
            if title:
                self.save_item(title, f)
            else:
                logging.debug(f'"{f}" didn\'t match any pattern')

    def parse(self, filename):
        d = guessit(filename, '-t movie')
        if d and d.get('title'):
            t = d['title']
            if d.get('part'):
                t += f' Part {d["part"]}'
            if d.get('year'):
                t += f" {d['year']}"
            return t        
        logging.info(f'{filename} doesn\'t look like a movie')

    def save_item(self, title: str, path: str):
        movie_id = self.lookup(title)
        if not movie_id:
            return

        with new_session() as session:
            movie = session.query(models.Movie).filter(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ).first()
            modified_time = self.get_file_modified_time(path)
            if movie and (movie.modified_time == modified_time) and movie.meta_data:
                return
            metadata = self.get_metadata(path)
            if not metadata:
                return
            e = models.Movie(
                movie_id=movie_id,
                path=path,
                meta_data=metadata,
                modified_time=modified_time,
            )
            session.merge(e)
            session.commit()
            logging.info(f'Saved movie: {title} (Id: {movie_id}) - Path: {path}')
            return True

    def lookup(self, title: str):
        logging.info(f'Looking for a movie with title: "{title}"')
        with new_session() as session:
            movie = session.query(models.Movie_id_lookup).filter(
                models.Movie_id_lookup.file_movie_title == title,
            ).first()
            if not movie:
                movies = self.client.get('/search', {
                    'title': title,
                    'type': 'movie',
                })
                if not movies:
                    logging.info(f'Didn\'t find a match for movie "{title}"')
                    return
                logging.info(f'Found movie: {movies[0]["title"]} (Id: {movies[0]["id"]})')
                movie = models.Movie_id_lookup(
                    file_movie_title=title,
                    movie_title=movies[0]["title"],
                    movie_id=movies[0]["id"],
                    updated_at=datetime.utcnow(),
                )
                session.merge(movie)
                session.commit()
                return movie.movie_id
            else:                
                logging.info(f'Found movie from cache: {movie.movie_title} (Id: {movie.movie_id})')
                return movie.movie_id

    def delete_item(self, title, path):        
        movie_id = self.lookup(title)
        with new_session() as session:
            m = session.query(
                models.Movie,
            ).filter(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ).first()
            if m:
                session.delete(m)
                session.commit()
                logging.info(f'Deleted movie: {title} (Id: {movie_id}) - Path: {path}')
                return True
        return False

class Series_scan(Play_scan):

    def __init__(self, scan_path):
        super().__init__(
            scan_path=scan_path,
            type_='series',
        )
        self.show_id = Show_id(scanner=self)
        self.episode_number = Episode_number(scanner=self)
        self.not_found_shows = []

    def scan(self):
        logging.info(f'Scanning: {self.scan_path}')
        files = self.get_files()
        for f in files:
            episode = self.parse(f)
            self.save_item(episode, f)

    def parse(self, filename):
        d = guessit(filename, '-t series --episode')
        if d and d.get('title'):
            if d.get('season') and d.get('episode'):            
                return Parsed_episode_season(
                    file_show_title=d['title'],
                    season=d['season'],
                    episode=d['episode'],
                )
            elif d.get('date'):
                return Parsed_episode_air_date(
                    file_show_title=d['title'],
                    air_date=d['date'].isoformat(),
                )
            elif d.get('episode'):
                return Parsed_episode_number(
                    file_show_title=d['title'],
                    number=d['episode'],
                )
        logging.info(f'{filename} doesn\'t look like an episode')

    def episode_show_id_lookup(self, episode):
        '''

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if episode.file_show_title in self.not_found_shows:
            return False
        logging.info('Looking for a show with title: "{}"'.format(
            episode.file_show_title
        ))
        show_id = self.show_id.lookup(episode.file_show_title)
        if show_id:
            logging.info('Found show: "{}" with show id: {}'.format(
                episode.file_show_title,
                show_id,
            ))
            episode.show_id = show_id
            return True
        else:
            self.not_found_shows.append(episode.file_show_title)
            logging.info('No show found for title: "{}"'.format(
                episode.file_show_title,
            ))
        return False

    def episode_number_lookup(self, episode):
        '''
        Tries to lookup the episode number of the episode.
        Sets the number in the episode object if successful.

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.show_id:
            return
        if isinstance(episode, Parsed_episode_number):
            return True
        value = self.episode_number.get_lookup_value(episode)
        logging.info('Looking for episode {} with show_id {}'.format(
            value,
            episode.show_id,
        ))
        number = self.episode_number.lookup(episode)
        if number:                
            logging.info('Found episode {} from {} with show_id {}'.format(
                number,
                value,
                episode.show_id,
            ))
            episode.number = number
            return True
        else:
            logging.info('No episode was found for {} with show_id {}'.format(
                value,
                episode.show_id,
            ))
        return False

    def save_item(self, episode, path):
        '''
        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.show_id:
            if not self.episode_show_id_lookup(episode):
                return False
        if not episode.number:
            if not self.episode_number_lookup(episode):
                return False
        with new_session() as session:
            ep = session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == episode.show_id,
                models.Episode.number == episode.number,
            ).first()
            modified_time = self.get_file_modified_time(path)
            if ep and (ep.modified_time == modified_time) and \
                (ep.path == path) and ep.meta_data:
                return
            metadata = self.get_metadata(path)
            e = models.Episode(
                show_id=episode.show_id,
                number=episode.number,
                path=path,
                meta_data=metadata,
                modified_time=modified_time,
            )
            session.merge(e)
            session.commit()
            logging.info('Saved episode: {} {}'.format(
                episode.file_show_title,
                episode.number
            ))
            return True

    def delete_item(self, episode, path):        
        '''
        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.show_id:
            if not self.episode_show_id_lookup(episode):
                return False
        if not episode.number:
            if not self.episode_number_lookup(episode):
                return False
        with new_session() as session:
            ep = session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == episode.show_id,
                models.Episode.number == episode.number,
            ).first()
            if ep:
                session.delete(ep)
                session.commit()
                logging.info('Deleted episode: {} {}'.format(
                    episode.file_show_title,
                    episode.number
                ))
                return True
        return False


class Parsed_episode(object):

    def __init__(self):
        self.lookup_type = 0
        self.show_id = None
        self.number = None

class Parsed_episode_season(Parsed_episode):

    def __init__(self, file_show_title, season, episode, show_id=None, number=None):
        super().__init__()
        self.lookup_type = 1
        self.file_show_title = file_show_title
        self.season = season
        self.episode = episode
        self.show_id = show_id
        self.number = number

class Parsed_episode_air_date(Parsed_episode):

    def __init__(self, file_show_title, air_date, show_id=None, number=None):
        super().__init__()
        self.lookup_type = 2
        self.file_show_title = file_show_title
        self.air_date = air_date
        self.show_id = show_id
        self.number = number

class Parsed_episode_number(Parsed_episode):

    def __init__(self, file_show_title, number, show_id=None):
        super().__init__()
        self.file_show_title = file_show_title
        self.number = number
        self.show_id = show_id

class Show_id(object):
    '''Used to lookup a show id by it's title.
    The result will be cached in the local db.
    '''

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, file_show_title):
        '''
        Tries to find the show on SEPLIS by it's title.

        :param file_show_title: str
        :returns: int
        '''
        show_id = self.db_lookup(file_show_title)
        if show_id:
            return show_id
        show = self.web_lookup(file_show_title)
        show_id = show['id'] if show else None
        show_title = show['title'] if show else None
        with new_session() as session:
            show = models.Show_id_lookup(
                file_show_title=file_show_title,
                show_title=show_title,
                show_id=show_id,
                updated=datetime.utcnow(),
            )
            session.merge(show)
            session.commit()
        return show_id

    def db_lookup(self, file_show_title):        
        '''

        :param file_show_title: str
        :returns: int
        '''
        with new_session() as session:
            show = session.query(
                models.Show_id_lookup
            ).filter(
                models.Show_id_lookup.file_show_title == file_show_title,
            ).first()
            if not show or not show.show_id:
                return
            return show.show_id

    def web_lookup(self, title):
        series = self.scanner.client.get('/search', {
            'title': title,
            'type': 'movie',
        })
        if not series:
            logging.info(f'Didn\'t find a match for series "{title}"')
            return
        logging.info(f'Found series: {series[0]["title"]} (Id: {series[0]["id"]})')
        return series[0]

class Episode_number(object):
    '''Used to lookup an episode's number from the season and episode or
    an air date.
    Stores the result in the local db.
    '''

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, episode):
        if not episode.show_id:
            raise Exception('show_id must be defined in the episode object')
        if isinstance(episode, Parsed_episode_number):
            return episode.number
        number = self.db_lookup(episode)
        if number:
            return number
        number = self.web_lookup(episode)
        if not number:
            return
        with new_session() as session:
            e = models.Episode_number_lookup(
                show_id=episode.show_id,
                lookup_type=episode.lookup_type,
                lookup_value=self.get_lookup_value(episode),
                number=number,
            )
            session.add(e)
            session.commit()
        return number

    def db_lookup(self, episode):
        with new_session() as session:
            value = self.get_lookup_value(episode)
            e = session.query(
                models.Episode_number_lookup.number
            ).filter(
                models.Episode_number_lookup.show_id == episode.show_id,
                models.Episode_number_lookup.lookup_type == episode.lookup_type,
                models.Episode_number_lookup.lookup_value == value,
            ).first()
            if not e:
                return
            return e.number

    @staticmethod
    def get_lookup_value(episode):
        value = None
        if isinstance(episode, Parsed_episode_season):
            value = '{}-{}'.format(
                episode.season,
                episode.episode,
            )
        elif isinstance(episode, Parsed_episode_air_date):
            value = '{}'.format(
                episode.air_date,
            )
        else:
            raise Exception('''
                Unknown parsed episode object. 
                If the episode already contains a number there is no need 
                to use this method.
            ''')
        return value

    def web_lookup(self, episode):
        if isinstance(episode, Parsed_episode_season):
            query = f'season:{episode.season} AND episode:{episode.episode}'
        elif isinstance(episode, Parsed_episode_air_date):
            query = f'air_date:{episode.air_date}'
        else:
            raise Exception('Unknown parsed episode object')
        episodes = self.scanner.client.get(f'/shows/{episode.show_id}/episodes', {
            'q': query,
            'fields': 'number',
        })
        if not episodes:
            return
        return episodes[0]['number']


def upgrade_scan_db():
    import alembic.config
    from alembic import command
    cfg = alembic.config.Config(
        os.path.dirname(
            os.path.abspath(__file__)
        )+'/alembic.ini'
    )
    cfg.set_main_option('script_location', 'seplis.play:migration')
    cfg.set_main_option('url', config.data.play.database)
    command.upgrade(cfg, 'head')