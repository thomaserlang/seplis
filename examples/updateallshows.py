import seplis
import logging
seplis.config_load()

indexer = seplis.Show_indexer(
    url=seplis.config['api']['url'], 
    access_token=seplis.config['client']['access_token']
)

shows = indexer.get('/shows?sort=id&per_page=500')
for show in shows.all():
    if show['id'] < 660:
        continue
    def index():
        try:
            indexer.update_show(show['id'])
            logging.error('updated show {}'.format(show['id']))
        except KeyboardInterrupt:
            raise
        except:
            logging.exception('error')
            index()
    index()