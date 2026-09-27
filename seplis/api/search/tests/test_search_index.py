from datetime import date
from typing import Any

import httpx
import pytest
import sqlalchemy as sa

from seplis.api.database import database
from seplis.api.movie import MMovie, MovieCreate, rebuild_movies, save_movie
from seplis.api.movie.actions.movie_actions import delete_movie
from seplis.api.search.actions import search_index_actions
from seplis.api.search.actions.search_actions import search_titles
from seplis.api.search.schemas.search_schemas import SearchTitleDocument
from seplis.api.series import MSeries, SeriesCreate, rebuild_series, save_series
from seplis.api.series.actions.series_actions import delete_series


async def lookup(title: str) -> list[SearchTitleDocument]:
    return await search_titles(query=None, title=title, title_type=None)


@pytest.mark.asyncio
async def test_immediate_changes_and_original_titles(db: None) -> None:
    movie = await save_movie(
        MovieCreate(
            title='Amelie',
            original_title='Le Fabuleux Destin',
            release_date=date(2001, 4, 25),
        )
    )
    assert (await lookup('le.fabuleux.destin (2001)'))[0].id == movie.id
    await save_movie({'title': 'Renamed'}, movie_id=movie.id)
    assert await lookup('Amelie') == []
    assert (await lookup('Renamed'))[0].id == movie.id
    await delete_movie(movie_id=movie.id)
    assert await lookup('Renamed') == []
    # Deleting an already missing search document is harmless.
    await search_index_actions.delete_document(f'movie-{movie.id}')

    series = await save_series(SeriesCreate(title='The Office'))
    assert (await lookup('The Office'))[0].id == series.id
    await save_series({'title': None}, series_id=series.id)
    assert await lookup('The Office') == []
    await save_series({'title': 'Renamed series'}, series_id=series.id)
    await delete_series(series.id)
    assert await lookup('Renamed series') == []


@pytest.mark.asyncio
async def test_bulk_refresh_paginates_and_updates_metadata(db: None) -> None:
    async with database.session() as session:
        await session.execute(
            sa.insert(MMovie),
            [
                {
                    'title': f'Bulk title {i}',
                    'popularity': 42,
                    'rating': 8.5,
                    'rating_votes': 123,
                }
                for i in range(105)
            ],
        )
    series = await save_series(SeriesCreate(title='Bulk series', popularity=1))
    async with database.session() as session:
        await session.execute(
            sa.update(MSeries).where(MSeries.id == series.id).values(popularity=99)
        )
    await rebuild_movies()
    await rebuild_series()
    for i in (0, 99, 100, 104):
        result = (await lookup(f'Bulk title {i}'))[0]
        assert result.popularity == 42
        assert result.rating == 8.5
        assert result.rating_votes == 123
    assert (await lookup('Bulk series'))[0].popularity == 99


@pytest.mark.asyncio
@pytest.mark.parametrize('body', ['{"success":false,"error":"bad field"}', ''])
async def test_import_checks_each_result(
    monkeypatch: pytest.MonkeyPatch, body: str
) -> None:
    async def response(*args: Any, **kwargs: Any) -> httpx.Response:
        return httpx.Response(200, text=body)

    monkeypatch.setattr(search_index_actions, 'request', response)
    with pytest.raises(RuntimeError, match='Search import failed'):
        await search_index_actions.import_documents('test', [{'id': 'movie-1'}])
