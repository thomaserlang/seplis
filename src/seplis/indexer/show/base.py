import tempfile
import os
import os.path
import time

indexers = {}

def register_indexer(class_):
    if class_.__indexer_name__ in indexers:
        raise Exception('{} is already registered as an indexer'.format(
            class_.__indexer_name__
        ))
    indexers[class_.__indexer_name__] = class_

class Show_indexer_base(object):

    def get_show(self, show_id):
        '''
        Override this function to return a show object.
        '''

    def get_episodes(self, show_id):
        '''
        Override this function to return a list of episodes.
        '''

    def get_images(self, show_id):
        '''
        Override this function to return a list of images.
        '''

    def get_updates(self):
        '''
        Override this function to return a list of show id's that
        should be updated.
        '''

    def get_latest_update_timestamp(self):
        '''

        :returns: float
        '''
        path = os.path.join(
            tempfile.gettempdir(),
            'seplis',
            'index',
            self.__indexer_name__+'.timestamp',
        )
        if not os.path.isfile(path):
            return time.time() - 86400
        with open(path, 'r') as f:
            return float(f.readline())

    def set_latest_update_timestamp(self, timestamp=None):
        '''

        :param timestamp: float
        :returns: float
        '''
        path = os.path.join(
            tempfile.gettempdir(),
            'seplis',
            'index',
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