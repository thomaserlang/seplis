import logging
import os
import time
from seplis import schemas, config

importers = {}

def register_importer(class_):
    if not class_.id:
        raise Exception('The importer id can\'t be `None`')
    if class_.id in importers:
        raise Exception('{} is already registered as an indexer'.format(
            class_.id
        ))
    importers[class_.id] = class_

class Show_importer_base(object):

    """The displayed name"""
    name = None
    """The key in externals for the show"""
    id = None
    """Tuple of supported import methods
        - info
        - episodes
        - images
    """
    supported = ()

    def info(self, show_id):
        """Override this function and return a show.
        The return result must match `schemas.Show`.
        """

    def episodes(self, show_id):
        """Override this function and return a list of episodes.
        The return result must match [`schemas.Episode`]
        """

    def images(self, show_id):
        """Override this function and return a list of images
        of the show.
        The return result must match [`schemas.Image_required`].

        The image will be downloaded from url in `source_url`.
        """

    def incremental_updates(self):
        """Override this function and return a list of show ids that has changed
        since last check.
        Use `last_update_timestamp` and `save_timestamp`.
        The return must be a list of str/int.
        """

    def last_update_timestamp(self):
        """Get the unix timestamp from when `incremental_updates()` was last run.
        For this to work it's required that `incremental_updates()`
        calls `save_timestamp()` after it's done.

        If there is no saved info it defaults to 24 hours ago.

        :returns: float
        """
        path = os.path.join(
            config['data_dir'],
            'importer',
            self.id+'.timestamp',
        )
        if not os.path.isfile(path):
            return time.time() - 86400
        with open(path, 'r') as f:
            return float(f.readline())

    def save_timestamp(self, timestamp):
        """Saves a timestamp in a file.
        If timestamp is `None` the current time will be used.

        The correct way to use this is to save the current timestamp
        to a variable. Do the work and then call `save_timestamp(timestamp)`.

        ```
        ttime = time.time()
        .. do the work
        self.save_timestamp(ttime)
        ```
        """
        path = os.path.join(
            config['data_dir'],
            'importer',
        )
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(
            path,
            self.id+'.timestamp',
        )
        if not timestamp:
            timestamp = time.time()
        with open(path, 'w') as f:
            f.write(str(timestamp))
        return timestamp