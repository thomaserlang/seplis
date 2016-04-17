
def update_show(access_token, show_id):
    import seplis.importer
    seplis.importer.shows.update_show_by_id(show_id)