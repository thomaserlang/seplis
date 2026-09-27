from datetime import UTC, date, datetime
from typing import Any
from unittest.mock import Mock

import httpx
import pytest
import respx
from pydantic import ValidationError

from seplis.api.common import validate_python
from seplis.api.page_cursor import PageCursor
from seplis.api.series import Episode, EpisodeUpdate, SeriesUpdate, save_series
from seplis.importer.movies.importer import get_movie_data
from seplis.importer.people.themoviedb import TheMovieDB as PeopleTMDB
from seplis.importer.series.themoviedb import TheMovieDB
from seplis.importer.series.thetvdb import Thetvdb
from seplis.importer.series.tvmaze import Tvmaze


async def assert_episodes_saved(
    client: httpx.AsyncClient, episodes: list[EpisodeUpdate]
) -> None:
    series = await save_series(
        SeriesUpdate(title='Imported series', episodes=episodes), patch=False
    )
    response = await client.get(f'/2/series/{series.id}/episodes')
    assert response.status_code == 200
    saved = validate_python(PageCursor[Episode], response.json()).records
    assert len(saved) == len(episodes)
    for actual, expected in zip(saved, episodes, strict=True):
        assert actual.air_date == expected['air_date']
        assert actual.air_datetime == expected['air_datetime']


@pytest.mark.asyncio
async def test_tmdb_episode_dates(
    client: httpx.AsyncClient, respx_mock: respx.MockRouter
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/tv/1').respond(
        200, json={'number_of_seasons': 1}
    )
    respx_mock.get('https://api.themoviedb.org/3/tv/1/season/1').respond(
        200,
        json={
            'episodes': [
                {
                    'name': ' Episode ',
                    'season_number': 1,
                    'episode_number': number,
                    'air_date': air_date,
                    'overview': None,
                }
                for number, air_date in enumerate(['1997-08-13', None, ''], 1)
            ]
        },
    )
    episodes = await TheMovieDB().episodes('1')
    assert episodes is not None
    assert episodes[0]['title'] == 'Episode'
    assert episodes[0]['air_date'] == date(1997, 8, 13)
    assert episodes[0]['air_datetime'] == datetime(1997, 8, 13, tzinfo=UTC)
    for episode in episodes[1:]:
        assert episode['air_date'] is None
        assert episode['air_datetime'] is None
    await assert_episodes_saved(client, episodes)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'timestamp',
    ['2004-01-23T17:00:00Z', '2004-01-23T17:00:00+00:00', '2004-01-23T19:00:00+02:00'],
)
async def test_tvmaze_episode_dates(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch, timestamp: str
) -> None:
    monkeypatch.setattr(
        'seplis.importer.series.tvmaze.requests.get',
        Mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        'name': 'Episode',
                        'season': 1,
                        'number': number,
                        'airdate': air_date,
                        'airstamp': air_datetime,
                        'summary': None,
                    }
                    for number, (air_date, air_datetime) in enumerate(
                        [('2004-01-23', timestamp), (None, None), ('', '')], 1
                    )
                ],
            )
        ),
    )
    episodes = await Tvmaze().episodes('1')
    assert episodes is not None
    assert episodes[0]['air_date'] == date(2004, 1, 23)
    assert episodes[0]['air_datetime'] == datetime(2004, 1, 23, 17, tzinfo=UTC)
    for episode in episodes[1:]:
        assert episode['air_date'] is None
        assert episode['air_datetime'] is None
    await assert_episodes_saved(client, episodes)


@pytest.mark.asyncio
@pytest.mark.parametrize('premiered', ['1997-08-13', None, ''])
async def test_series_metadata_dates(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch, premiered: str | None
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/tv/1').respond(
        200,
        json={
            'id': 1,
            'name': ' Series ',
            'original_name': ' Series ',
            'overview': None,
            'genres': [],
            'status': 'Returning Series',
            'episode_run_time': ['30'],
            'first_air_date': premiered,
            'original_language': 'en',
            'popularity': '1.5',
            'tagline': None,
        },
    )
    monkeypatch.setattr(
        'seplis.importer.series.tvmaze.requests.get',
        Mock(
            return_value=httpx.Response(
                200,
                json={
                    'id': 1,
                    'externals': {},
                    'name': ' Series ',
                    'summary': None,
                    'status': 'Running',
                    'runtime': '30',
                    'genres': [],
                    'premiered': premiered,
                    'language': 'English',
                },
            )
        ),
    )
    for provider in (TheMovieDB(), Tvmaze()):
        info = await provider.info('1')
        assert info is not None
        assert info['title'] == 'Series'
        assert info['runtime'] == 30
        assert info['premiered'] == (date(1997, 8, 13) if premiered else None)


def test_tvdb_episode_validation() -> None:
    episode = {
        'episodeName': ' Episode ',
        'absoluteNumber': '1',
        'airedSeason': '1',
        'airedEpisodeNumber': '1',
        'firstAired': '2004-01-23',
    }
    episodes = Thetvdb().parse_episodes([episode, {**episode, 'absoluteNumber': '-1'}])
    assert episodes == [
        {
            'title': 'Episode',
            'original_title': 'Episode',
            'plot': None,
            'number': 1,
            'season': 1,
            'episode': 1,
            'air_date': date(2004, 1, 23),
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize('birthday,deathday', [('1950-01-01', '2020-02-03'), (None, '')])
async def test_person_metadata_dates(
    respx_mock: respx.MockRouter, birthday: str | None, deathday: str | None
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/person/1').respond(
        200,
        json={
            'id': 1,
            'name': ' Person ',
            'also_known_as': [],
            'birthday': birthday,
            'deathday': deathday,
            'gender': '2',
            'biography': None,
            'place_of_birth': None,
            'popularity': '1.5',
        },
    )
    info = await PeopleTMDB().info('1')
    assert info is not None
    assert info['name'] == 'Person'
    assert info['birthday'] == (date(1950, 1, 1) if birthday else None)
    assert info['deathday'] == (date(2020, 2, 3) if deathday else None)
    assert info['gender'] == 2
    assert info['popularity'] == 1.5


@pytest.fixture
def movie_payload() -> dict[str, Any]:
    return {
        'title': ' Movie ',
        'original_title': ' Movie ',
        'status': 'Released',
        'runtime': '90',
        'release_date': '2004-01-23',
        'overview': '',
        'tagline': '',
        'original_language': 'en',
        'genres': [],
        'popularity': '1.5',
        'revenue': '100',
        'budget': '50',
        'belongs_to_collection': None,
    }


@pytest.mark.asyncio
async def test_movie_metadata_types(
    respx_mock: respx.MockRouter, movie_payload: dict[str, Any]
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/movie/1').respond(
        200, json=movie_payload
    )
    info = await get_movie_data('1')
    assert info is not None
    assert info['title'] == 'Movie'
    assert info['release_date'] == date(2004, 1, 23)
    assert info['runtime'] == 90
    assert info['popularity'] == 1.5
    assert info['revenue'] == 100
    assert info['budget'] == 50


@pytest.mark.asyncio
async def test_movie_metadata_rejects_invalid_values(
    respx_mock: respx.MockRouter, movie_payload: dict[str, Any]
) -> None:
    respx_mock.get('https://api.themoviedb.org/3/movie/1').respond(
        200, json={**movie_payload, 'budget': -1}
    )
    with pytest.raises(ValidationError):
        await get_movie_data('1')


@pytest.mark.asyncio
async def test_series_cast_types(respx_mock: respx.MockRouter) -> None:
    respx_mock.get('https://api.themoviedb.org/3/tv/1/aggregate_credits').respond(
        200,
        json={
            'cast': [
                {
                    'id': 1,
                    'roles': [{'character': ' Role ', 'episode_count': '3'}],
                    'order': '0',
                    'total_episode_count': '3',
                }
            ]
        },
    )
    assert await TheMovieDB().cast('1') == [
        {
            'external_name': 'themoviedb',
            'external_id': '1',
            'roles': [{'character': 'Role', 'total_episodes': 3}],
            'order': 0,
            'total_episodes': 3,
        }
    ]


@pytest.mark.asyncio
async def test_tmdb_lookup_returns_string_id(respx_mock: respx.MockRouter) -> None:
    respx_mock.get('https://api.themoviedb.org/3/find/tt1234567').respond(
        200, json={'tv_results': [{'id': 123}]}
    )
    assert await TheMovieDB().lookup_from_imdb('tt1234567') == '123'
