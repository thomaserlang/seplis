import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_episode_to_watch(client: AsyncClient):
    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
            schemas.Episode_create(number=3, title='3', runtime=40),
        ]
    ), series_id=None)

    r = await client.get(f'/2/series/{series.id}/episodes')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_result[schemas.Episode].model_validate(r.json())
    for episode in data.items:
        assert episode.user_watched == None

    
    r = await client.get(f'/2/series/{series.id}/episodes', params={
        'expand': 'user_watched'
    })
    assert r.status_code == 401

    await user_signin(client)
    
    r = await client.get(f'/2/series/{series.id}/episodes', params={
        'expand': 'something, user_watched'
    })
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Episode].model_validate(r.json())
    for episode in data.items:
        assert episode.user_watched.times == 0

    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.get(f'/2/series/{series.id}/episodes', params={
        'expand': 'user_watched'
    })
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Episode].model_validate(r.json())
    for episode in data.items:
        if episode.number == 1:
            assert episode.user_watched.times == 1
        else:
            assert episode.user_watched.times == 0


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient):
    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
            schemas.Episode_create(number=3, title='3'),
            schemas.Episode_create(number=4, title='4'),
            schemas.Episode_create(number=5, title='5'),
        ]
    ), series_id=None)

    r = await client.get(f'/2/series/{series.id}/episodes', params={
        'per_page': 1,
    })
    data = schemas.Page_cursor_result[schemas.Episode].model_validate(r.json())
    assert len(data.items) == 1
    assert data.items[0].number == 1
    assert len(data.cursor) > 1

    r = await client.get(f'/2/series/{series.id}/episodes', params={
        'per_page': 1,
        'cursor': data.cursor,
    })
    data = schemas.Page_cursor_result[schemas.Episode].model_validate(r.json())
    assert len(data.items) == 1
    assert data.items[0].number == 2


if __name__ == '__main__':
    run_file(__file__)