import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from seplis import logger

@pytest.mark.asyncio
async def test_user_series_following(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
            schemas.Episode_create(title='Episode 2', number=2),
        ]
    ), series_id=None)
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
            schemas.Episode_create(title='Episode 2', number=2),
        ]
    ), series_id=None)

    r = await client.get('/2/users/me/series-watched')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 0

    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    
    r = await client.get('/2/users/me/series-watched')
    assert r.status_code == 200, r.content
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 1
    assert data.items[0].series.id == series1.id
    assert data.items[0].last_episode_watched.number == 1

    
    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.get('/2/users/me/series-watched')
    assert r.status_code == 200, r.content
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 2
    assert data.items[0].series.id == series2.id
    assert data.items[0].last_episode_watched.number == 2
    assert data.items[1].series.id == series1.id
    assert data.items[1].last_episode_watched.number == 1


if __name__ == '__main__':
    run_file(__file__)