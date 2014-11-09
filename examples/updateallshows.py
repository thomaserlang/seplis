import seplis
import logging
seplis.config_load()

indexer = seplis.Show_indexer(
    url=seplis.config['client']['api_url'], 
    access_token=seplis.config['client']['access_token']
)

shows = indexer.get('/shows?sort=id&per_page=500')
for show in shows.all():
    indexer.update_show(show['id'])
    logging.info('updated show {}'.format(show['id']))