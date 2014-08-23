import seplis
seplis.config_load()

indexer = seplis.Show_indexer(
    url=seplis.config['api']['url'], 
    access_token=seplis.config['client']['access_token']
)

print(indexer.new(
    external_name='tvrage',
    external_id='4628',
))