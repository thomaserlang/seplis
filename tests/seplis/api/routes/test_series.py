import io
import pytest, respx, httpx
from seplis.api import constants
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis import config

@pytest.mark.asyncio
@respx.mock
async def test_series(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_DELETE_SHOW)])

    r = await client.post('/2/series', json={})
    assert r.status_code == 201, r.content
    assert r.json()['id'] > 0

    r = await client.post('/2/series', json={
        'title': 'QWERTY',
        'description': {
            'text': 'The cases of the Naval Criminal Investigative Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
            'title': 'IMDb',
            'url': 'http://www.imdb.com/title/tt123456799/',
        },
        'premiered': '2003-01-01',
        'ended': None,
        'importers': {
            'info': 'imdb',
            'episodes': 'imdb',
        },
        'externals': {
            'imdb': 'tt123456799',
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
    data = r.json()
    series_id = data['id']

    r = await client.get(f'/2/series/{series_id}')
    data = r.json()
    assert r.status_code == 200, r.content
    assert data['title'], 'QWERTY'
    assert data['description'], {
        'text': 'The cases of the Naval Criminal Investigative Service. \\_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
        'title': 'IMDb',
        'url': 'http://www.imdb.com/title/tt123456799/',
    }
    assert data['premiered'] == '2003-01-01'
    assert data['premiered'] == '2003-01-01'
    assert data['ended'] == None
    assert data['importers'] == {
        'info': 'imdb',
        'episodes': 'imdb',
    }
    assert data['externals'] == {
        'imdb': 'tt123456799',
    }
    assert 'Action' in data['genres']
    assert 'Thriller' in data['genres']
    assert 'QWERTY 2' in data['alternative_titles']
    assert 'QWERTY 3' in data['alternative_titles']
    assert data['runtime'] == 40
    assert data['episode_type'] == constants.SHOW_EPISODE_TYPE_SEASON_EPISODE
    assert data['seasons'] == []

    r = await client.get(f'/2/series/externals/imdb/tt123456799')
    data = r.json()
    assert r.status_code == 200, r.content
    assert data['title'], 'QWERTY'
    
    r = await client.patch(f'/2/series/{series_id}', json={
        'title': 'QWERTY2',
        'description': {
            'text': 'The cases of the Naval Criminal Investigative Service.',
        },
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
    data = r.json()
    assert data['title'] == 'QWERTY2'
    assert data['description']['text'] == 'The cases of the Naval Criminal Investigative Service.'
    assert data['premiered'] == '2003-01-01'
    assert data['ended'] == None
    assert data['importers'] == {
        'info': 'imdb',
        'episodes': 'tvmaze',
    }
    assert data['externals'] == {
        'imdb': 'tt123456799',
    }
    assert data['episode_type'] == constants.SHOW_EPISODE_TYPE_AIR_DATE
    assert 'Action' in data['genres']
    assert 'Thriller' in data['genres']

    r = await client.patch(f'/2/series/{series_id}', json={
        'title': 'QWERTY2',
        'description': {
            'text': 'The cases of the Naval Criminal Investigative Service.',
        },
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
    data = r.json()
    assert 'Action' in data['genres']
    assert 'Thriller' in data['genres']
    assert 'Comedy' in data['genres']

    r = await client.put(f'/2/series/{series_id}', json={
        'title': 'QWERTY2',
        'description': {
            'text': 'Something something',
        },
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
    data = r.json()
    assert 'Action' in data['genres']
    assert 'Thriller' not in data['genres']
    assert 'Comedy' in data['genres']
    assert data['importers'] == {
        'info': 'tvmaze',
        'episodes': 'tvmaze',
    }    
    assert data['externals'] == {
        'imdb': 'tt123456797',
    }
    assert data['premiered'] == '2003-01-02'
    
    r = await client.get(f'/2/series/externals/imdb/tt123456797')
    data = r.json()
    assert r.status_code == 200, r.content
    assert data['title'], 'QWERTY2'

    # it should be possible to set both the importer and the external
    # value to None.        
    r = await client.patch(f'/2/series/{series_id}', json={
        'importers':{
            'info': None,
        },
        'externals': {
            'imdb': None,
        }
    })
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['externals'] == {}
    assert data['importers'] == {
        'info': None,
        'episodes': 'tvmaze',
    }

    r = await client.get(f'/2/series/externals/imdb/tt123456797')
    data = r.json()
    assert r.status_code == 404, r.content

    r = await client.put(f'/2/series/{series_id}', json={
        'episode_type': constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
    })
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['episode_type'] == constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER

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
                'description': {
                    'text': 'Test description.'
                }
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
    series = r.json()
    assert series['seasons'] == [
        {'total': 2, 'season': 1, 'to': 2, 'from': 1}, 
        {'total': 1, 'season': 2, 'to': 3, 'from': 3},
    ]

    r = await client.put(f'/2/series/{series_id}', json={
        'alternative_titles': [
            'test',
            'test',
            'test2'
        ],
    })
    assert r.status_code == 200, r.content
    series = r.json()
    assert series['alternative_titles'].sort() == [
        'test',
        'test2'
    ].sort()

    r = await client.put(f'/2/series/{series_id}', json={
        'alternative_titles': [],
    })
    assert r.status_code == 200, r.content
    series = r.json()
    assert series['alternative_titles'] == []

    r = await client.get(f'/2/series/{series_id}/episodes?per_page=1')
    assert r.status_code == 200, r.content
    episodes = r.json()
    assert len(episodes['items']) == 1, episodes
    assert episodes['items'][0]['number'] == 1
    
    r = await client.get(f'/2/series/{series_id}/episodes?per_page=1&page=2')
    assert r.status_code == 200, r.content
    episodes = r.json()
    assert len(episodes['items']) == 1, episodes
    assert episodes['items'][0]['number'] == 2

    r = await client.get(f'/2/series/{series_id}/episodes?season=1')
    assert r.status_code == 200, r.content
    episodes = r.json()
    assert len(episodes['items']) == 2, episodes
    assert episodes['items'][0]['number'] == 1
    assert episodes['items'][1]['number'] == 2

    r = await client.get(f'/2/series/{series_id}/episodes?season=2')
    assert r.status_code == 200, r.content
    episodes = r.json()
    assert len(episodes['items']) == 1, episodes
    assert episodes['items'][0]['number'] == 3

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 200, r.content

    r = await client.delete(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/3')
    assert r.status_code == 404, r.content

    config.data.api.storitch = 'http://storitch'
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
    assert r.status_code == 400, r.content

    respx.put("http://storitch/store/session").mock(return_value=httpx.Response(200, json={
        'type': 'image',
        'width': 1000,
        'height': 680,
        'hash': '8b31b97a043ef44b3073622ed00fa6aafc89422d0c3a926a3f6bc30ddfb1f492',
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
    data = r.json()
    assert data['id'] > 0
    assert data['width'] == 1000
    assert data['height'] == 680
    assert data['hash'] == '8b31b97a043ef44b3073622ed00fa6aafc89422d0c3a926a3f6bc30ddfb1f492'
    assert data['type'] == 'poster'

    # Test duplicate
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
    assert r.status_code == 400, r.content
    
    r = await client.get(f'/2/series/{series_id}/images')
    assert r.status_code == 200
    data = r.json()
    assert data['total'] == 1
    assert data['items'][0]['id'] > 0


    poster_image_id = data['items'][0]['id']
    r = await client.put(f'/2/series/{series_id}', json={
        'poster_image_id': poster_image_id,
    })
    assert r.status_code == 200

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['poster_image']['id'] == poster_image_id

    r = await client.delete(f'/2/series/{series_id}/images/{poster_image_id}')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['poster_image'] == None


    r = await client.delete(f'/2/series/{series_id}')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series_id}/episodes/2')
    assert r.status_code == 404, r.content

    r = await client.get(f'/2/series/{series_id}')
    assert r.status_code == 404, r.content


if __name__ == '__main__':
    run_file(__file__)