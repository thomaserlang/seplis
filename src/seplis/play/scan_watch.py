import logging, time
import asyncio
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

    def __init__(self, scan_path, loop, type_='shows'):
        logging.debug('initiated')
        patterns = ['*.'+t for t in config['play']['media_types']]
        super().__init__(
            patterns=patterns,
        )
        self.type = type_
        self.loop = loop
        self.wait_list = {}
        if type_ == 'shows':
            self.scanner = scan.Shows_scan(scan_path=scan_path)
        else:
            raise NotImplemented('Type: {} is not supported for watching'.format(
                type_
            ))

    def parse(self, event):
        if event.is_directory:
            logging.info('{} is a directory, skipping'.format(event.src_path))
            return
        path = event.src_path
        if event.event_type == 'moved':
            path = event.dest_path
        if self.type == 'shows':
            episode = scan.parse_episode(path)
            if not episode:
                logging.info('{} could not be parsed'.format(event.src_path))
                return
            return episode
        else:
            raise NotImplemented('Type: {} is not supported for watching'.format(
                type_
            ))        

    def update(self, event):
        item = self.parse(event)
        if not item:
            return
        self.scanner.save_item(item)

    def delete(self, event):
        logging.debug('Delete: {}'.format(event.src_path))        

    def on_created(self, event):
        self.update(event)

    def on_deleted(self, event):
        item = self.parse(event)
        if not item:
            return
        self.scanner.delete_item(item)

    def on_moved(self, event):
        self.update(event)

    def on_modified(self, event):
        self.loop.call_soon_threadsafe(self._modified, event)

    def _modified(self, event):
        if event.src_path in self.wait_list:
            self.wait_list[event.src_path].cancel()
        self.wait_list[event.src_path] = self.loop.call_later(
            5, 
            self.update, 
            event
        )


def main():
    if not config['play']['scan']:
        raise Exception('''
            Nothing to scan. Add a path in the config file.

            Example:

                play:
                    scan:
                        -
                            type: shows
                            path: /a/path/to/the/shows
            ''')
    obs = Observer()
    loop = asyncio.get_event_loop()
    for s in config['play']['scan']:
        event_handler = Handler(
            scan_path=s['path'],
            type_=s['type'],
            loop=loop,
        )
        obs.schedule(
            event_handler,
            s['path'],
            recursive=True,
        )
    obs.start()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        obs.stop()
        loop.stop()
    obs.join()
    loop.close()