import io
import pytest, respx, httpx
from seplis.api import constants
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis import config

@pytest.mark.asyncio
@respx.mock
async def test_movie(client: AsyncClient):
    await user_signin(client, scopes=[str(constants.LEVEL_DELETE_SHOW)])
    r = await client.get('/2/movies/1')
    assert r.status_code == 404, r.content

    r = await client.post('/2/movies', json={
        'title': 'National Treasure',
        'externals': {
            'imdb': 'tt0368891',
        },
        'alternative_titles': [
            'National Treasure 2004',
        ]
    })
    assert r.status_code == 201, r.content
    data = r.json()
    movie_id = data['id']
    assert data['id'] > 0
    assert data['title'] == 'National Treasure'
    assert data['externals']['imdb'] == 'tt0368891'
    assert data['alternative_titles'] == ['National Treasure 2004']

    r = await client.get(f'/2/movies/{movie_id}')
    assert r.status_code == 200
    data = r.json()
    assert data['title'] == 'National Treasure'
    assert data['externals']['imdb'] == 'tt0368891'

    r = await client.patch(f'/2/movies/{movie_id}', json={
        'externals': {
            'themoviedb': '12345',
        },
        'alternative_titles': [
            'National Treasure test',
        ]
    })
    assert r.status_code == 200
    data = r.json()
    assert data['title'] == 'National Treasure'
    assert data['externals']['imdb'] == 'tt0368891'
    assert data['externals']['themoviedb'] == '12345'
    assert sorted(data['alternative_titles']) == sorted(['National Treasure test', 'National Treasure 2004'])


    r = await client.put(f'/2/movies/{movie_id}', json={
        'externals': {
            'themoviedb': '12345',
        },
        'alternative_titles': [],
    })
    assert r.status_code == 200
    data = r.json()
    assert data['title'] == 'National Treasure'
    assert 'imdb' not in data['externals']
    assert data['externals']['themoviedb'] == '12345'
    assert data['alternative_titles'] == []

    r = await client.get(f'/2/movies/{movie_id}')
    assert r.status_code == 200
    data = r.json()
    assert data['alternative_titles'] == []


    config.data.api.storitch = 'http://storitch'
    r = await client.post(f'/2/movies/{movie_id}/images', 
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
    r = await client.post(f'/2/movies/{movie_id}/images', 
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
    r = await client.post(f'/2/movies/{movie_id}/images', 
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

    r = await client.get(f'/2/movies/{movie_id}/images')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['total'] == 1
    assert data['items'][0]['id'] > 0

    poster_image_id = data['items'][0]['id']
    r = await client.put(f'/2/movies/{movie_id}', json={
        'poster_image_id': poster_image_id,
    })
    assert r.status_code == 200

    r = await client.get(f'/2/movies/{movie_id}')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['poster_image']['id'] == poster_image_id
    
    r = await client.delete(f'/2/movies/{movie_id}/images/{poster_image_id}')
    assert r.status_code == 204

    r = await client.get(f'/2/movies/{movie_id}')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data['poster_image'] == None


    r = await client.delete(f'/2/movies/{movie_id}')
    assert r.status_code == 204

    r = await client.get(f'/2/movies/{movie_id}')
    assert r.status_code == 404, r.content


if __name__ == '__main__':
    run_file(__file__)