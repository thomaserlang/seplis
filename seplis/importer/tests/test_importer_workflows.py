from collections.abc import AsyncIterator
from datetime import date
from importlib import import_module
from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from seplis.api.contexts import AsyncSession
from seplis.api.movie import MovieCreate, save_movie
from seplis.api.movie.actions.movie_cast_actions import save_movie_cast
from seplis.api.person import PersonCreate, save_person
from seplis.api.series import (
    SeriesCreate,
    SeriesUpdate,
    save_series,
)
from seplis.api.series.actions.series_cast_actions import add_series_cast
from seplis.importer.movies import importer as movie_importer
from seplis.importer.people import importer as people_importer
from seplis.importer.series import importer as series_importer
from seplis.importer.themoviedb_export import IdData


@pytest.mark.asyncio
@pytest.mark.parametrize('aliases', [[], ['Alias']])
async def test_create_person_and_skip_unchanged_metadata(
    client: httpx.AsyncClient,
    respx_mock: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
    aliases: list[str],
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/person/1').respond(
        200,
        json={
            'id': 1,
            'name': 'Person',
            'also_known_as': aliases,
            'birthday': '1950-01-01',
            'deathday': '2020-02-03',
            'gender': 2,
            'biography': 'Biography',
            'place_of_birth': 'Birthplace',
            'popularity': 1.5,
            'profile_path': None,
        },
    )
    person = await people_importer.create_person('themoviedb', '1')
    assert person is not None
    assert person.id is not None
    assert person.name == 'Person'
    assert person.birthday == date(1950, 1, 1)
    assert person.deathday == date(2020, 2, 3)
    assert person.externals == {'themoviedb': '1'}
    assert person.also_known_as == aliases

    save = AsyncMock()
    monkeypatch.setattr(people_importer, 'save_person', save)
    assert await people_importer.update_person_info(person) is None
    save.assert_not_awaited()


@pytest.mark.asyncio
async def test_series_cast_compares_imported_roles_with_stored_roles(
    client: httpx.AsyncClient,
    respx_mock: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    series = await save_series(
        SeriesCreate(title='Series', externals={'themoviedb': '1'})
    )
    person = await save_person(PersonCreate(name='Person', externals={'themoviedb': '2'}))
    assert person.id is not None
    await add_series_cast(
        series_id=series.id,
        data={
            'person_id': person.id,
            'order': 0,
            'total_episodes': 3,
            'roles': [{'character': 'Role', 'total_episodes': 3}],
        },
    )
    route = respx_mock.get('https://api.themoviedb.org/3/tv/1/aggregate_credits')
    cast = {
        'id': 2,
        'order': 0,
        'total_episode_count': 3,
        'roles': [{'character': 'Role', 'episode_count': 3}],
    }
    route.respond(200, json={'cast': [cast]})
    save = AsyncMock(wraps=add_series_cast)
    monkeypatch.setattr(series_importer, 'add_series_cast', save)
    await series_importer.update_series_cast(series)
    save.assert_not_awaited()

    route.respond(
        200,
        json={
            'cast': [{**cast, 'roles': [{'character': 'New role', 'episode_count': 3}]}]
        },
    )
    await series_importer.update_series_cast(series)
    save.assert_awaited_once()
    assert save.call_args.kwargs['data']['roles'] == [
        {'character': 'New role', 'total_episodes': 3}
    ]


@pytest.mark.asyncio
async def test_popularity_creates_series_with_importer_settings(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    popularity = import_module('seplis.importer.series.update_popularity')

    async def get_ids(export: str) -> AsyncIterator[IdData]:
        yield IdData(id=1, original_title='Series', popularity=2.0)

    monkeypatch.setattr(popularity, 'get_ids', get_ids)
    monkeypatch.setattr(
        popularity.TheMovieDB,
        'info',
        AsyncMock(
            return_value=SeriesUpdate(
                title='Series', externals={'themoviedb': '1', 'imdb': 'tt1234567'}
            )
        ),
    )
    # Keep the popularity job inside the test fixture's rollback transaction.
    monkeypatch.setattr(AsyncSession, 'commit', AsyncMock())
    monkeypatch.setattr(popularity, 'rebuild_series', AsyncMock())
    update = AsyncMock()
    monkeypatch.setattr(series_importer, 'update_series', update)

    await popularity.update_popularity()

    update.assert_awaited_once()
    series = update.call_args.kwargs['series']
    assert series.id is not None
    assert series.importers.info == 'themoviedb'
    assert series.importers.episodes == 'themoviedb'


@pytest.mark.asyncio
@pytest.mark.parametrize('character', [' Role ', ''])
async def test_movie_cast_normalizes_values_before_comparing(
    client: httpx.AsyncClient,
    respx_mock: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
    character: str,
) -> None:
    movie = await save_movie(MovieCreate(title='Movie', externals={'themoviedb': '1'}))
    person = await save_person(PersonCreate(name='Person', externals={'themoviedb': '2'}))
    assert person.id is not None
    await save_movie_cast(
        movie_id=movie.id,
        data={
            'person_id': person.id,
            'order': 0,
            'character': character.strip() or None,
        },
    )
    route = respx_mock.get('https://api.themoviedb.org/3/movie/1/credits')
    cast = {'id': 2, 'name': 'Person', 'order': '0', 'character': character}
    route.respond(200, json={'cast': [cast]})
    save = AsyncMock(wraps=save_movie_cast)
    monkeypatch.setattr(movie_importer, 'save_movie_cast', save)

    await movie_importer.update_cast(movie)
    save.assert_not_awaited()

    route.respond(200, json={'cast': [{**cast, 'order': '1'}]})
    await movie_importer.update_cast(movie)
    save.assert_awaited_once()
    assert save.call_args.kwargs['data']['order'] == 1
