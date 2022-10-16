import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_episode_watched(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1),
            schemas.Episode_create(number=2),
            schemas.Episode_create(number=3, runtime=40),
        ]
    ), series_id=None)


    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at != None


    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at != None

    
    r = await client.delete(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at != None

    r = await client.delete(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 204, r.content


    r = await client.post(f'/2/series/{series.id}/episodes/watched-range', json={
        'from_episode_number': 1,
        'to_episode_number': 3,
    })
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 1

    r = await client.get(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 1

    r = await client.get(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.times == 1


if __name__ == '__main__':
    run_file(__file__)