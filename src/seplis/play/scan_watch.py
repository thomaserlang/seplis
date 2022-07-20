import logging, time
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
from seplis.play import scan
from seplis import config

class Handler(PatternMatchingEventHandler):

    def __init__(self, scan_path, type_='series'):
        logging.debug('initiated')
        patterns = ['*.'+t for t in config.data.play.media_types]
        super().__init__(
            patterns=patterns,
        )
        self.type = type_
        self.wait_list = {}
        if type_ == 'series':
            self.scanner = scan.Series_scan(scan_path=scan_path)
        elif type_ == 'movies':
            self.scanner = scan.Movie_scan(scan_path=scan_path)
        else:
            raise NotImplemented(f'Type: {type_} is not supported for watching')

    def parse(self, event):
        if event.is_directory:
            logging.info(f'{event.src_path} is a directory, skipping')
            return
        path = event.src_path
        if event.event_type == 'moved':
            path = event.dest_path
        return (self.scanner.parse(path), path)
            
    def update(self, event):
        try:
            item = self.parse(event)
            if item:
                self.scanner.save_item(item[0], item[1])
        except:
            logging.exception('update') 

    def on_created(self, event):
        self.update(event)

    def on_deleted(self, event):
        try:
            item = self.parse(event)
            if item:
                self.scanner.delete_item(item[0], item[1])
        except:
            logging.exception('on_deleted')

    def on_moved(self, event):
        event.event_type = 'deleted'
        try:
            item = self.parse(event)
            if item:
                self.scanner.delete_item(item[0], item[1])
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
                            path: /a/path/to/the/series
            ''')
    
    obs = Observer()
    logging.info('Play scan watch started')
    for s in config.data.play.scan:
        logging.info(f'Watching: {s.path}')
        event_handler = Handler(
            scan_path=str(s.path),
            type_=s.type,
        )
        obs.schedule(
            event_handler,
            str(s.path),
            recursive=True,
        )
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
    logging.info('Play scan watch stopped')