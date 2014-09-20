
def update_show(access_token, show_id):
    from seplis import config
    from seplis.indexer import Show_indexer
    indexer = Show_indexer(    
        url=config['api']['url'], 
        access_token=access_token,
    )
    indexer.update_show(show_id)