import logging, time
import asyncio, functools
try:
    from watchdog.observers import Observer  
    from watchdog.events import PatternMatchingEventHandler  
except ImportError:
    raise ImportError(
'''Install the watchdog package.

    pip install watchdog
'''
)
from seplis.play import scan
from seplis import config

class Handler(PatternMatchingEventHandler):

    def __init__(self, scan_path, type_='shows'):
        logging.debug('initiated')
        patterns = ['*.'+t for t in config.data.play.media_types]
        super().__init__(
            patterns=patterns,
        )
        self.type = type_
        self.wait_list = {}
        if type_ == 'shows':
            self.scanner = scan.Shows_scan(scan_path=scan_path)
        else:
            raise NotImplemented(f'Type: {type_} is not supported for watching')

    def parse(self, event):
        if event.is_directory:
            logging.info(f'{event.src_path} is a directory, skipping')
            return
        path = event.src_path
        if event.event_type == 'moved':
            path = event.dest_path
        if self.type == 'shows':
            episode = scan.parse_episode(path)
            if not episode:
                logging.info(f'{event.src_path} could not be parsed')
                return
            return episode
            
    def update(self, event):
        try:
            item = self.parse(event)
            if not item:
                return
            self.scanner.save_item(item)
        except:
            logging.exception('update') 

    def on_created(self, event):
        self.update(event)

    def on_deleted(self, event):
        try:
            item = self.parse(event)
            if not item:
                return
            self.scanner.delete_item(item)
        except:
            logging.exception('on_deleted')

    def on_moved(self, event):
        event.event_type = 'deleted'
        try:
            item = self.parse(event)
            if item:
                self.scanner.delete_item(item)
            event.event_type = 'moved'
            self.update(event)
        except:
            logging.exception('on_moved')

def main():
    if not config.data.play.scan:
        raise Exception('''
            Nothing to scan. Add a path in the config file.

            Example:

                play:
                    scan:
                        -
                            type: series | movies
                            path: /a/path/to/the/shows
            ''')
    
    obs = Observer()
    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info('Play scan watch started')
    for s in config.data.play.scan:    
        log.info(s)
        event_handler = Handler(
            scan_path=s['path'],
            type_=s['type'],
        )
        obs.schedule(
            event_handler,
            s['path'],
            recursive=True,
        )
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
    log.info('Play scan watch stopped')