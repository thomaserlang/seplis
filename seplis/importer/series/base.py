import os, os.path
import time
import httpx
from seplis import config
from seplis.api import schemas
from typing import Literal

importers = {}

client = httpx.AsyncClient()

def register_importer(obj):
    if not isinstance(obj, Series_importer_base):
        raise Exception('The object must be an instance of `Show_importer_base()`')
    if not obj.external_name:
        raise Exception('The importer external_name can\'t be `None`')
    if obj.external_name in importers:
        raise Exception(f'{obj.external_name} is already registered as an indexer')
    importers[obj.external_name] = obj

class Series_importer_base(object):
    display_name: str
    external_name: str
    supported: tuple[Literal['info', 'episodes', 'images']]

    async def info(self, external_id: str) -> schemas.Series_update:
        """Override this function and return a show.
        The return result must match `schemas.Show`.
        """

    async def episodes(self, external_id: str) -> list[schemas.Episode_update]:
        """Override this function and return a list of episodes.
        The return result must match [`schemas.Episode`]
        """

    async def images(self, external_id: str) -> list[schemas.Image_import]:
        """Override this function and return a list of images
        of the show.
        The return result must match [`schemas.Image_required`].

        The image will be downloaded from url in `source_url`.
        """

    async def incremental_updates(self) -> list[str]:
        """Override this function and return a list of ids that has changed
        since last check.
        Use `last_update_timestamp` and `save_timestamp`.
        """

    def last_update_timestamp(self) -> int:
        """Get the unix timestamp from when `incremental_updates()` was last run.
        For this to work it's required that `incremental_updates()`
        calls `save_timestamp()` after it's done.

        If there is no saved info it defaults to 24 hours ago.

        :returns: int
        """
        path = os.path.expanduser(os.path.join(
            config.data.data_dir,
            'importer',
            self.external_name+'.timestamp',
        ))
        if not os.path.isfile(path):
            return int(time.time()) - 86400
        with open(path, 'r') as f:
            return int(f.readline())

    def save_timestamp(self, timestamp) -> int:
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
        path = os.path.expanduser(os.path.join(
            config.data.data_dir,
            'importer',
        ))
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(
            path,
            self.external_name+'.timestamp',
        )
        if not timestamp:
            timestamp = int(time.time())
        with open(path, 'w') as f:
            f.write(str(int(timestamp)))
        return timestamp