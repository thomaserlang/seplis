import io
import pytest
import respx
import httpx
from seplis.api import constants, schemas, models
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis import config
from datetime import date


@pytest.mark.asyncio
@respx.mock
async def test_series_create(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_DELETE_SHOW)])

    r = await client.post('/2/series', json={})
    assert r.status_code == 201, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.id > 0

    r = await client.post('/2/series', json={
        'title': 'QWERTY',
        'plot': 'The cases of the Naval Criminal Investigative Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
        'premiered': '2003-01-01',
        'ended': None,
        'importers': {
            'info': 'imdb',
            'episodes': 'imdb',
        },
        'externals': {
            'imdb': 'tt123456799',
            'no': None
        },
        'genres': [
            'Action',
            'Thriller',
        ],
        'alternative_titles': [
            'QWERTY 2',
            'QWERTY 3',
        ],
        'runtime': 40,
    })
    assert r.status_code == 201, r.content
    data = schemas.Series.parse_obj(r.json())
    series_id = data.id

    r = await client.get(f'/2/series/{series_id}')
    data = schemas.Series.parse_obj(r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY'
    assert data.plot == 'The cases of the Naval Criminal Investigative Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ'
    assert data.premiered == date(2003, 1, 1)
    assert data.ended == None
    assert data.importers == {
        'info': 'imdb',
        'episodes': 'imdb',
    }
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

    r = await client.get(f'/2/series/externals/imdb/tt123456799')
    data = schemas.Series.parse_obj(r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY'

    r = await client.patch(f'/2/series/{series_id}', json={
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
        'genres': [
            'Action',
        ],
    })
    assert r.status_code == 200, r.content
    r = await client.patch(f'/2/series/{series_id}', json={
        'importers': {
            'episodes': 'tvmaze'
        }
    })
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.title == 'QWERTY2'
    assert data.plot == 'The cases of the Naval Criminal Investigative Service.'
    assert data.premiered == date(2003, 1, 1)
    assert data.ended == None
    assert data.importers == {
        'info': 'imdb',
        'episodes': 'tvmaze',
    }
    assert data.externals == {
        'imdb': 'tt123456799',
    }
    assert data.episode_type == constants.SHOW_EPISODE_TYPE_AIR_DATE
    assert 'Action' == data.genres[0].name
    assert 'Thriller' == data.genres[1].name

    r = await client.patch(f'/2/series/{series_id}', json={
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
        'genres': [
            'Action',
            'Comedy'
        ],
    })
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert 'Action' == data.genres[0].name
    assert 'Comedy' == data.genres[1].name
    assert 'Thriller' == data.genres[2].name

    r = await client.put(f'/2/series/{series_id}', json={
        'title': 'QWERTY2',
        'plot': 'Something something',
        'premiered': '2003-01-02',
        'importers': {
            'info': 'tvmaze',
        },
        'externals': {
            'imdb': 'tt123456797',
        },
        'genres': [
            'Action',
            'Comedy'
        ],
    })
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert 'Action' == data.genres[0].name
    assert 'Comedy' == data.genres[1].name
    assert len(data.genres) == 2
    assert data.importers == {
        'info': 'tvmaze',
        'episodes': 'tvmaze',
    }
    assert data.externals == {
        'imdb': 'tt123456797',
    }
    assert data.premiered == date(2003, 1, 2)

    r = await client.get(f'/2/series/externals/imdb/tt123456797')
    data = schemas.Series.parse_obj(r.json())
    assert r.status_code == 200, r.content
    assert data.title, 'QWERTY2'

    # it should be possible to set both the importer and the external
    # value to None.
    r = await client.patch(f'/2/series/{series_id}', json={
        'importers': {
            'info': None,
        },
        'externals': {
            'imdb': None,
        }
    })
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.externals == {}
    assert data.importers == {
        'info': None,
        'episodes': 'tvmaze',
    }

    r = await client.get(f'/2/series/externals/imdb/tt123456797')
    assert r.status_code == 404, r.content

    r = await client.put(f'/2/series/{series_id}', json={
        'episode_type': constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
    })
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.episode_type == constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER

    r = await client.put(f'/2/series/{series_id}', json={
        'episode_type': 999,
    })
    assert r.status_code == 422, r.content

    r = await client.put(f'/2/series/{series_id}', json={
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
    })
    assert r.status_code == 200, r.content
    series = schemas.Series.parse_obj(r.json())
    assert series.seasons == [
        schemas.Series_season(total=2, season=1, to=2, from_=1),
        schemas.Series_season(total=1, season=2, to=3, from_=3),
    ]

    r = await client.put(f'/2/series/{series_id}', json={
        'alternative_titles': [
            'test',
            'test',
            'test2'
        ],
    })
    assert r.status_code == 200, r.content
    series = schemas.Series.parse_obj(r.json())
    assert series.alternative_titles.sort() == [
        'test',
        'test2'
    ].sort()

    r = await client.put(f'/2/series/{series_id}', json={
        'alternative_titles': [],
    })
    assert r.status_code == 200, r.content
    series = schemas.Series.parse_obj(r.json())
    assert series.alternative_titles == []

    r = await client.get(f'/2/series/{series_id}/episodes?season=1')
    assert r.status_code == 200, r.content
    episodes = schemas.Page_cursor_result[schemas.Episode].parse_obj(r.json())
    assert len(episodes.items) == 2, episodes
    assert episodes.items[0].number == 1
    assert episodes.items[1].number == 2

    r = await client.get(f'/2/series/{series_id}/episodes?season=2')
    assert r.status_code == 200, r.content
    episodes = schemas.Page_cursor_result[schemas.Episode].parse_obj(r.json())
    assert len(episodes.items) == 1, episodes
    assert episodes.items[0].number == 3

    r = await client.get(f'/2/series/{series_id}/episodes?air_date=2014-01-01')
    assert r.status_code == 200, r.content
    episodes = schemas.Page_cursor_result[schemas.Episode].parse_obj(r.json())
    assert len(episodes.items) == 1, episodes
    assert episodes.items[0].number == 1

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 200, r.content

    r = await client.delete(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 404, r.content

    config.data.api.storitch_host = 'http://storitch'
    r = await client.post(f'/2/series/{series_id}/images',
                          files={
                              'image': io.BytesIO(b"some initial text data"),
                          },
                          data={
                              'type': 'wronga',
                              'external_name': 'seplis',
                              'external_id': 'test',
                          }
                          )
    assert r.status_code == 422, r.status_code

    respx.post("http://storitch/store/session").mock(return_value=httpx.Response(200, json={
        'type': 'image',
        'width': 1000,
        'height': 680,
        'hash': '8b31b97a043ef44b3073622ed00fa6aafc89422d0c3a926a3f6bc30ddfb1f492',
        'file_id': '1a4dd776-f82f-4df7-893a-c03a168bc90d',
    }))
    r = await client.post(f'/2/series/{series_id}/images',
                          files={
                              'image': io.BytesIO(b"some initial text data"),
                          },
                          data={
                              'type': 'poster',
                              'external_name': 'seplis',
                              'external_id': 'test',
                          }
                          )
    assert r.status_code == 201, r.content
    data = schemas.Image.parse_obj(r.json())
    assert data.id > 0
    assert data.width == 1000
    assert data.height == 680
    assert data.file_id == '1a4dd776-f82f-4df7-893a-c03a168bc90d'
    assert data.type == 'poster'

    # Test duplicate
    # Should just return the duplicated image
    r = await client.post(f'/2/series/{series_id}/images',
                          files={
                              'image': io.BytesIO(b"some initial text data"),
                          },
                          data={
                              'type': 'poster',
                              'external_name': 'seplis',
                              'external_id': 'test',
                          }
                          )
    assert r.status_code == 201, r.content
    data = schemas.Image.parse_obj(r.json())
    assert data.file_id == '1a4dd776-f82f-4df7-893a-c03a168bc90d'

    r = await client.get(f'/2/series/{series_id}/images')
    assert r.status_code == 200
    data = schemas.Page_cursor_total_result[schemas.Image].parse_obj(r.json())
    assert data.total == 1
    assert data.items[0].id > 0

    poster_image_id = data.items[0].id
    r = await client.put(f'/2/series/{series_id}', json={
        'poster_image_id': poster_image_id,
    })
    assert r.status_code == 200

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.poster_image.id == poster_image_id

    r = await client.delete(f'/2/series/{series_id}/images/{poster_image_id}')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = schemas.Series.parse_obj(r.json())
    assert data.poster_image == None

    r = await client.delete(f'/2/series/{series_id}')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/2')
    assert r.status_code == 404, r.content

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 404, r.content


@pytest.mark.asyncio
@respx.mock
async def test_series_get(client: AsyncClient):
    r = await client.get(f'/2/series')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert data.items == []

    series1 = await models.Series.save(data=schemas.Series_create(
        title="Test 1",
        genres=['Test1'],
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
        ],
    ))
    series2 = await models.Series.save(data=schemas.Series_create(
        title="Test 2",
        genres=['Test2'],
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
            schemas.Episode_create(title='Episode 2', number=2),
        ],
    ))

    r = await client.get(f'/2/series?user_watchlist=true')
    assert r.status_code == 401

    user_id = await user_signin(client, [str(constants.LEVEL_USER)])

    await models.Series_watchlist.add(series_id=series1.id, user_id=user_id)

    r = await client.get(f'/2/series?user_watchlist=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series1.id

    r = await client.get(f'/2/series?user_watchlist=false')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series2.id

    r = await client.get(f'/2/series?sort=user_last_episode_watched_at_asc')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 0

    r = await client.get(f'/2/series?expand=user_watchlist')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 2
    data.items[0].user_watchlist.on_watchlist == True
    data.items[1].user_watchlist.on_watchlist == False

    await models.Episode_watched.increment(series_id=series2.id, episode_number=1, user_id=user_id, data=schemas.Episode_watched_increment())

    r = await client.get(f'/2/series?user_has_watched=true&expand=user_last_episode_watched')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series2.id
    assert data.items[0].user_last_episode_watched.number == 1

    r = await client.get(f'/2/series?user_has_watched=false')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series1.id

    r = await client.get(f'/2/series', params={
        'not_genre_id': series1.genres[0].id,
        'genre_id': series2.genres[0].id,
    })
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series2.id


if __name__ == '__main__':
    run_file(__file__)
