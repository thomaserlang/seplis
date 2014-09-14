import seplis
import logging
seplis.config_load()

indexer = seplis.Show_indexer(
    url=seplis.config['api']['url'], 
    access_token=seplis.config['client']['access_token']
)

shows = indexer.get('/shows?sort=id&per_page=500')
for show in shows.all():
    retries = 0
    def index(retries):
        try:
            indexer.update_show(show['id'])
            logging.error('updated show {}'.format(show['id']))
        except KeyboardInterrupt:
            raise
        except:
            logging.exception('error')
            if retries <= 5:
                retries += 1
                index(retries)
    index(retries)