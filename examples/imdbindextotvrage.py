from seplis import Client, config, config_load
config_load()

client = Client(
    url=config['client']['api_url'], 
    access_token=config['client']['access_token']
)

shows = client.get('/shows?q=info:thetvdb&per_page=500&sort=id')
for show in shows.all():
    client.patch('/shows/{}'.format(show['id']), {
        'indices': {
            'episodes': 'thetvdb',
        }
    })