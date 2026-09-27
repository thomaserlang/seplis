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

from ..models.series_model import MSeries
from ..schemas.series_schemas import Series
from .series_mapping import select_series, series_row_mapper


async def save_series_for_search(series: Series) -> None:
    document = series_title_document_mapper(series)
    if not document:
        await delete_document(f'series-{series.id}')
        return
    await write_documents([index_document(document, series.original_title)])


def series_title_document_mapper(series: Series) -> SearchTitleDocument | None:
    if not series.title:
        return None
    titles = [series.title, series.original_title, *(series.alternative_titles or [])]
    return SearchTitleDocument(
        type='series',
        id=series.id,
        title=series.title,
        titles=[SearchTitleDocumentTitle(title=t) for t in dict.fromkeys(titles) if t],
        release_date=series.premiered,
        imdb=(series.externals or {}).get('imdb'),
        poster_image=series.poster_image,
        popularity=float(series.popularity or 0),
        genres=series.genres,
        rating=float(series.rating) if series.rating is not None else None,
        rating_votes=series.rating_votes,
        episodes=series.total_episodes,
        seasons=len(series.seasons or []),
        runtime=series.runtime,
        language=series.language,
    )


async def rebuild_series(collection: str | None = None) -> None:
    last_id = 0
    while True:
        # Live refreshes read and index under the same lock as individual writes.
        async with index_lock() if collection is None else nullcontext():
            async with database.session() as session:
                result = await session.execute(
                    select_series()
                    .where(MSeries.id > last_id)
                    .order_by(MSeries.id)
                    .limit(1000 if collection else 100)
                )
                rows = result.mappings().all()
            if not rows:
                return
            documents = []
            for row in rows:
                item = series_row_mapper(row)
                last_id = item.id
                document = series_title_document_mapper(item)
                if document:
                    documents.append(index_document(document, item.original_title))
            if collection:
                await import_documents(collection, documents)
            else:
                await write_documents_locked(documents)
