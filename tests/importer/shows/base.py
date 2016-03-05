
class Show_importer_base(object):

    """The name display to the user when choosing importer source"""
    name = None
    """Must match the externals key from the show"""
    id = None
    """"""
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
        """Override this function and return a list of show ids.
        The return must be a list of [str/int].
        """

    def last_update_timestamp(self):
        """Get the timestamp from when update last was run.
        For this to work it's required that `incremental_updates`
        calls `save_timestamp` after it's work is done.
        """

    def save_timestamp(self, timestamp=None):
        """Saves a timestamp in a file.
        If timestamp i none the current timestamp will be used.

        The correct way to use this is to save the current timestamp
        to a variable. Do the work and the call `save_timestamp(timestamp)`.

        ```
        ttime = time.time()
        .. do the work
        self.save_timestamp(ttime)
        ```
        """
        path = os.path.join(
            tempfile.gettempdir(),
            'seplis',
            'index',
        )
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(
            path,
            self.__indexer_name__+'.timestamp',
        )
        if not timestamp:
            timestamp = time.time()
        with open(path, 'w') as f:
            f.write(str(timestamp))
        return timestamp