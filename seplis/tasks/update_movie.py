
async def update_movie(ctx, movie_id):
    import seplis.importer
    await seplis.importer.movies.update_movie(movie_id=movie_id)