import logging
from seplis.api import constants
from seplis import schemas, config

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
            self.name+'.timestamp',
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
            self.name+'.timestamp',
        )
        if not timestamp:
            timestamp = time.time()
        with open(path, 'w') as f:
            f.write(str(timestamp))
        return timestamp

    @classmethod
    def info_changes(cls, show_original, show_new):
        """Compares two show dicts for changes.
        If the return is an empty dict there is no
        difference between the two.

        :returns: dict
        """
        changes = {}
        skip_fields = (
            'externals',
            'indices',
            'episodes',
        )
        for s in schemas._Show_schema:
            if not isinstance(s, str) or s in skip_fields:
                continue
            if s in show_original and s in show_new:
                if show_original[s] == None and isinstance(show_new[s], dict):
                    continue
                if show_original[s] != show_new[s]:
                    if isinstance(show_original[s], list):
                        changes[s] = list(set(show_new[s]) - set(show_original[s]))
                        if not changes[s]:
                            changes.pop(s)
                    else:
                        changes[s] = show_new[s]
            elif s not in show_original and s in show_new:
                changes[s] = show_new[s]
        return changes

    @classmethod
    def episode_changes(cls, episodes_original, episodes_new):
        """Compares two episode list of dicts for changes.
        If the return is an empty list there is no
        difference between the two.

        :returns: list of dict
        """
        changes = []
        current = {episode['number']: episode for episode in episodes_original}
        for episode in episodes_new:
            data = {}
            current_episode = current[episode['number']] if episode['number'] in current else episode 
            if episode['number'] not in current:
                changes.append(episode)
                continue
            for s in schemas._Episode_schema:
                s = str(s)
                if s == 'number':
                    data[s] = episode[s]
                    continue
                if s in episode and s in current_episode:
                    if episode[s] == None and isinstance(current_episode[s], dict):
                        continue
                    if episode[s] != current_episode[s]:
                        data[s] = episode[s]
                elif s not in current_episode and s in episode:
                    data[s] = episode[s]
            if data != {} and len(data) > 1:
                changes.append(data)
        return changes