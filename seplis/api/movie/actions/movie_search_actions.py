from contextlib import nullcontext

from seplis.api.database import database
from seplis.api.search import SearchTitleDocument, SearchTitleDocumentTitle
from seplis.api.search.actions.search_index_actions import (
    delete_document,
    import_documents,
    index_lock,
    write_documents,
    write_documents_locked,
)
from seplis.api.search.actions.search_mapping import index_document

from ..models.movie_model import MMovie
from ..schemas.movie_schemas import Movie
from .movie_mapping import movie_row_mapper, select_movies


async def save_movie_for_search(movie: Movie) -> None:
    document = movie_title_document_mapper(movie)
    if not document:
        await delete_document(f'movie-{movie.id}')
        return
    await write_documents([index_document(document, movie.original_title)])


def movie_title_document_mapper(movie: Movie) -> SearchTitleDocument | None:
    if not movie.title:
        return None
    titles = [movie.title, movie.original_title, *(movie.alternative_titles or [])]
    return SearchTitleDocument(
        type='movie',
        id=movie.id,
        title=movie.title,
        titles=[SearchTitleDocumentTitle(title=t) for t in dict.fromkeys(titles) if t],
        release_date=movie.release_date,
        imdb=(movie.externals or {}).get('imdb'),
        poster_image=movie.poster_image,
        popularity=float(movie.popularity or 0),
        genres=movie.genres,
        rating=float(movie.rating) if movie.rating is not None else None,
        rating_votes=movie.rating_votes,
        runtime=movie.runtime,
        language=movie.language,
    )


async def rebuild_movies(collection: str | None = None) -> None:
    last_id = 0
    while True:
        # Live refreshes read and index under the same lock as individual writes.
        async with index_lock() if collection is None else nullcontext():
            async with database.session() as session:
                result = await session.execute(
                    select_movies()
                    .where(MMovie.id > last_id)
                    .order_by(MMovie.id)
                    .limit(100)
                )
                rows = result.mappings().all()
            if not rows:
                return
            documents = []
            for row in rows:
                item = movie_row_mapper(row)
                last_id = item.id
                document = movie_title_document_mapper(item)
                if document:
                    documents.append(index_document(document, item.original_title))
            if collection:
                await import_documents(collection, documents)
            else:
                await write_documents_locked(documents)
