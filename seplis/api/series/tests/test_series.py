import io
from datetime import date

import httpx
import pytest
import respx
from pydantic import AnyHttpUrl

from seplis import config
from seplis.api import constants
from seplis.api.image import Image
from seplis.api.page_cursor import PageCursor
from seplis.api.series import (
    Episode,
    EpisodeCreate,
    Series,
    SeriesCreate,
    SeriesSeason,
    add_series_watchlist,
    save_series,
)
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin  # noqa


@pytest.mark.asyncio
@respx.mock
async def test_series_create(client: AsyncClient) -> None:
    await user_signin(
        client, ['series:create', 'series:edit', 'series:delete', 'series:manage_images']
    )

    r = await client.post('/2/series', json={})
    assert r.status_code == 201, r.content
    data = parse_obj_as(Series, r.json())
    assert data.id > 0

    r = await client.post(
        '/2/series',
        json={
            'title': 'QWERTY',
            'plot': (
                'The cases of the Naval Criminal Investigative '
                'Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ'
            ),
            'premiered': '2003-01-01',
            'ended': None,
            'importers': {
                'info': 'imdb',
                'episodes': 'imdb',
            },
            'externals': {'imdb': 'tt123456799', 'no': None},
            'genre_names': [
                'Action',
                'Thriller',
            ],
            'alternative_titles': [
                'QWERTY 2',
                'QWERTY 3',
            ],
            'runtime': 40,
            'popularity': 4728.432,
            'rating': 7.5,
            'rating_votes': 3000,
        },
    )
    assert r.status_code == 201, r.content
    data = parse_obj_as(Series, r.json())
    series_id = data.id

    r = await client.get(f'/2/series/{series_id}')
    data = parse_obj_as(Series, r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY'
    assert data.plot == (
        'The cases of the Naval Criminal Investigative '
        'Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ'
    )
    assert data.premiered == date(2003, 1, 1)
    assert data.ended is None
    assert data.importers.info == 'imdb'
    assert data.importers.episodes == 'imdb'
    assert data.externals == {
        'imdb': 'tt123456799',
    }
    assert 'Action' == data.genres[0].name
    assert 'Thriller' == data.genres[1].name
    assert 'QWERTY 2' in data.alternative_titles
    assert 'QWERTY 3' in data.alternative_titles
    assert data.runtime == 40
    assert data.episode_type == constants.SHOW_EPISODE_TYPE_SEASON_EPISODE
    assert data.seasons == []

    r = await client.get('/2/series/externals/imdb/tt123456799')
    data = parse_obj_as(Series, r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY'

    r = await client.patch(
        f'/2/series/{series_id}',
        json={
            'title': 'QWERTY2',
            'plot': 'The cases of the Naval Criminal Investigative Service.',
            'premiered': '2003-01-01',
            'importers': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
            },
            'episode_type': constants.SHOW_EPISODE_TYPE_AIR_DATE,
            'genre_names': [
                'Action',
            ],
        },
    )
    assert r.status_code == 200, r.content
    r = await client.patch(
        f'/2/series/{series_id}', json={'importers': {'episodes': 'tvmaze'}}
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert data.title == 'QWERTY2'
    assert data.plot == 'The cases of the Naval Criminal Investigative Service.'
    assert data.premiered == date(2003, 1, 1)
    assert data.ended is None
    assert data.importers.info == 'imdb'
    assert data.importers.episodes == 'tvmaze'
    assert data.externals == {
        'imdb': 'tt123456799',
    }
    assert data.episode_type == constants.SHOW_EPISODE_TYPE_AIR_DATE
    assert 'Action' == data.genres[0].name
    assert 'Thriller' == data.genres[1].name

    r = await client.patch(
        f'/2/series/{series_id}',
        json={
            'title': 'QWERTY2',
            'plot': 'The cases of the Naval Criminal Investigative Service.',
            'premiered': '2003-01-01',
            'importers': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
            },
            'episode_type': constants.SHOW_EPISODE_TYPE_AIR_DATE,
            'genre_names': ['Action', 'Comedy'],
        },
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert 'Action' == data.genres[0].name
    assert 'Comedy' == data.genres[1].name
    assert 'Thriller' == data.genres[2].name

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'title': 'QWERTY2',
            'plot': 'Something something',
            'premiered': '2003-01-02',
            'importers': {
                'info': 'tvmaze',
            },
            'externals': {
                'imdb': 'tt123456797',
            },
            'genre_names': ['Action', 'Comedy'],
        },
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert 'Action' == data.genres[0].name
    assert 'Comedy' == data.genres[1].name
    assert len(data.genres) == 2
    assert data.importers.info == 'tvmaze'
    assert data.importers.episodes == 'tvmaze'
    assert data.externals == {
        'imdb': 'tt123456797',
    }
    assert data.premiered == date(2003, 1, 2)

    r = await client.get('/2/series/externals/imdb/tt123456797')
    data = parse_obj_as(Series, r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY2'

    # it should be possible to set both the importer and the external
    # value to None.
    r = await client.patch(
        f'/2/series/{series_id}',
        json={
            'importers': {
                'info': None,
            },
            'externals': {
                'imdb': None,
            },
        },
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert data.externals == {}
    assert data.importers.info is None
    assert data.importers.episodes == 'tvmaze'

    r = await client.get('/2/series/externals/imdb/tt123456797')
    assert r.status_code == 404, r.content

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'episode_type': constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
        },
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert data.episode_type == constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'episode_type': 999,
        },
    )
    assert r.status_code == 422, r.content

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'season': 1,
                    'plot': 'Test description.',
                },
                {
                    'number': 2,
                    'season': 1,
                    'title': 'Episode 2',
                },
                {
                    'number': 3,
                    'title': 'Episode 2',
                    'season': 2,
                },
            ]
        },
    )
    assert r.status_code == 200, r.content
    series = parse_obj_as(Series, r.json())
    assert series.seasons == [
        SeriesSeason(total=2, season=1, to=2, from_=1),
        SeriesSeason(total=1, season=2, to=3, from_=3),
    ]

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'alternative_titles': ['test', 'test', 'test2'],
        },
    )
    assert r.status_code == 200, r.content
    series = parse_obj_as(Series, r.json())
    assert series.alternative_titles.sort() == ['test', 'test2'].sort()

    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'alternative_titles': [],
        },
    )
    assert r.status_code == 200, r.content
    series = parse_obj_as(Series, r.json())
    assert series.alternative_titles == []

    r = await client.get(f'/2/series/{series_id}/episodes?season=1')
    assert r.status_code == 200, r.content
    episodes = parse_obj_as(PageCursor[Episode], r.json())
    assert len(episodes.records) == 2, episodes
    assert episodes.records[0].number == 1
    assert episodes.records[1].number == 2

    r = await client.get(f'/2/series/{series_id}/episodes?season=2')
    assert r.status_code == 200, r.content
    episodes = parse_obj_as(PageCursor[Episode], r.json())
    assert len(episodes.records) == 1, episodes
    assert episodes.records[0].number == 3

    r = await client.get(f'/2/series/{series_id}/episodes?air_date=2014-01-01')
    assert r.status_code == 200, r.content
    episodes = parse_obj_as(PageCursor[Episode], r.json())
    assert len(episodes.records) == 1, episodes
    assert episodes.records[0].number == 1

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 200, r.content

    r = await client.delete(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 404, r.content

    config.api.storitch_host = AnyHttpUrl('http://storitch')
    r = await client.post(
        f'/2/series/{series_id}/images',
        files={
            'image': io.BytesIO(b'some initial text data'),
        },
        data={
            'type': 'wronga',
            'external_name': 'seplis',
            'external_id': 'test',
        },
    )
    assert r.status_code == 422, r.content

    respx.post('http://storitch/store/session').mock(
        return_value=httpx.Response(
            200,
            json={
                'type': 'image',
                'width': 1000,
                'height': 680,
                'hash': (
                    '8b31b97a043ef44b3073622ed00fa6aafc89422d0c3a926a3f6bc30ddfb1f492'
                ),
                'file_id': '1a4dd776-f82f-4df7-893a-c03a168bc90d',
            },
        )
    )
    r = await client.post(
        f'/2/series/{series_id}/images',
        files={
            'image': io.BytesIO(b'some initial text data'),
        },
        data={
            'type': 'poster',
            'external_name': 'seplis',
            'external_id': 'test',
        },
    )
    assert r.status_code == 201, r.content
    data = parse_obj_as(Image, r.json())
    assert data.id > 0
    assert data.width == 1000
    assert data.height == 680
    assert data.file_id == '1a4dd776-f82f-4df7-893a-c03a168bc90d'
    assert data.type == 'poster'

    # Test duplicate
    # Should just return the duplicated image
    r = await client.post(
        f'/2/series/{series_id}/images',
        files={
            'image': io.BytesIO(b'some initial text data'),
        },
        data={
            'type': 'poster',
            'external_name': 'seplis',
            'external_id': 'test',
        },
    )
    assert r.status_code == 201, r.content
    data = parse_obj_as(Image, r.json())
    assert data.file_id == '1a4dd776-f82f-4df7-893a-c03a168bc90d'

    r = await client.get(f'/2/series/{series_id}/images')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Image], r.json())
    assert data.total == 1
    assert data.records[0].id > 0

    poster_image_id = data.records[0].id
    r = await client.put(
        f'/2/series/{series_id}',
        json={
            'poster_image_id': poster_image_id,
        },
    )
    assert r.status_code == 200

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert data.poster_image
    assert data.poster_image.id == poster_image_id

    r = await client.delete(f'/2/series/{series_id}/images/{poster_image_id}')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = parse_obj_as(Series, r.json())
    assert data.poster_image is None

    r = await client.delete(f'/2/series/{series_id}')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/2')
    assert r.status_code == 404, r.content

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 404, r.content


@pytest.mark.asyncio
@respx.mock
async def test_series_get(client: AsyncClient) -> None:
    r = await client.get('/2/series')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert data.records == []

    series1 = await save_series(
        data=SeriesCreate(
            title='Test 1',
            genre_names=['Test1'],
            episodes=[
                EpisodeCreate(title='Episode 1', number=1),
            ],
        )
    )
    series2 = await save_series(
        data=SeriesCreate(
            title='Test 2',
            genre_names=['Test2'],
            episodes=[
                EpisodeCreate(title='Episode 1', number=1),
                EpisodeCreate(title='Episode 2', number=2),
            ],
        )
    )

    r = await client.get('/2/series?user_watchlist=true')
    assert r.status_code == 401

    user_id = await user_signin(client, ['user:progress'])

    await add_series_watchlist(series_id=series1.id, user_id=user_id)

    r = await client.get('/2/series?user_watchlist=true')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series1.id

    r = await client.get('/2/series?user_watchlist=false')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series2.id

    r = await client.get('/2/series?sort=user_last_episode_watched_at_asc')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 0

    r = await client.get('/2/series?expand=user_watchlist')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 2
    assert data.records[0].user_watchlist
    assert data.records[0].user_watchlist.on_watchlist
    assert data.records[1].user_watchlist
    assert not data.records[1].user_watchlist.on_watchlist

    r = await client.post(f'/2/series/{series2.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.get(
        '/2/series?user_has_watched=true&expand=user_last_episode_watched'
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series2.id
    assert data.records[0].user_last_episode_watched
    assert data.records[0].user_last_episode_watched.number == 1

    r = await client.get('/2/series?user_has_watched=false')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series1.id

    r = await client.get(
        '/2/series',
        params={
            'not_genre_id': series1.genres[0].id,
            'genre_id': series2.genres[0].id,
        },
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series2.id


if __name__ == '__main__':
    run_file(__file__)
