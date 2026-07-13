from typing import Any


async def update_movie(ctx: dict[str, Any], movie_id: int) -> None:
    import seplis.importer

    await seplis.importer.movies.update_movie(movie_id=movie_id)
