import time
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
from seplis.play import scan
from seplis import config, logger

class Handler(PatternMatchingEventHandler):

    def __init__(self, scan_path, type_, make_thumbnails=False):
        logger.info(f'Watching {type_}: {scan_path}')
        patterns = ['*.'+t for t in config.data.play.media_types]
        super().__init__(patterns=patterns)
        self.type = type_
        self.wait_list = {}
        if type_ == 'series':
            self.scanner = scan.Series_scan(scan_path=scan_path, make_thumbnails=make_thumbnails)
        elif type_ == 'movies':
            self.scanner = scan.Movie_scan(scan_path=scan_path, make_thumbnails=make_thumbnails)
        else:
            raise Exception(f'Type: {type_} is not supported for watching')

    def parse(self, event):
        if event.is_directory:
            logger.info(f'{event.src_path} is a directory, skipping')
            return
        path = event.src_path
        if event.event_type == 'moved':
            path = event.dest_path        
        logger.info(event.key)
        return (self.scanner.parse(path), path)
            
    def update(self, event):
        try:
            item = self.parse(event)
            if item:
                self.scanner.save_item(item[0], item[1])
        except:
            logger.exception('update') 

    def on_created(self, event):
        self.update(event)

    def on_deleted(self, event):
        try:
            item = self.parse(event)
            if item:
                self.scanner.delete_item(item[0], item[1])
        except:
            logger.exception('on_deleted')

    def on_moved(self, event):
        event.event_type = 'deleted'
        try:
            item = self.parse(event)
            if item:
                self.scanner.delete_item(item[0], item[1])
            event.event_type = 'moved'
            self.update(event)
        except:
            logger.exception('on_moved')

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
    logger.info('Play scan watch started')
    for s in config.data.play.scan:
        event_handler = Handler(
            scan_path=str(s.path),
            type_=s.type,
            make_thumbnails=s.make_thumbnails,
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
    logger.info('Play scan watch stopped')