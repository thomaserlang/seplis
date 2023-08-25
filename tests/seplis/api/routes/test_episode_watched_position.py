import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_episode_watched_position(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
        ]
    ), series_id=None)

    url = f'/2/series/{series.id}/episodes/1/watched-position'
    # Return 204 if the episode has not been watched
    r = await client.get(url)
    assert r.status_code == 204, r.content

    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content
    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Episode_watched.model_validate(r.json())  
    assert w.times == 0
    assert w.position == 200
    assert w.watched_at != None

    r = await client.put(url, json={'position': 201})
    assert r.status_code == 204, r.content
    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Episode_watched.model_validate(r.json())
    assert w.times == 0
    assert w.position == 201       
    assert w.watched_at != None

    r = await client.delete(url)
    assert r.status_code == 204, r.content
    r = await client.get(url)
    assert r.status_code == 204, r.content


    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content
    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Episode_watched.model_validate(r.json())
    assert w.position == 200

    r = await client.put(url, json={'position': 0})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    assert r.status_code == 204, r.content


    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content
    r = await client.get(url)
    w = schemas.Episode_watched.model_validate(r.json())
    assert w.times == 1
    assert w.position == 200

    r = await client.delete(url)
    assert r.status_code == 204, r.content
    
    r = await client.get(url)
    w = schemas.Episode_watched.model_validate(r.json())
    assert w.times == 1
    assert w.position == 0


if __name__ == '__main__':
    run_file(__file__)