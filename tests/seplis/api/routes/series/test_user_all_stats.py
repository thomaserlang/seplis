import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_series_user_stats(client: AsyncClient):
    await user_signin(client)

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
            schemas.Episode_create(number=3, title='3', runtime=40),
        ]
    ), series_id=None)
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
        ]
    ), series_id=None)


    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 0
    assert data.episodes_watched_minutes == 0
    assert data.series_finished == 0
    assert data.series_watched == 0
    assert data.series_watchlist == 0
    

    await client.put(f'/2/series/{series1.id}/watchlist')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.series_watchlist == 1


    await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 1
    assert data.episodes_watched_minutes == 30
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 2
    assert data.episodes_watched_minutes == 60
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/2/watched')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 3
    assert data.episodes_watched_minutes == 90
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/3/watched')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 4
    assert data.episodes_watched_minutes == 130
    assert data.series_watched == 1
    assert data.series_finished == 1

    await client.post(f'/2/series/{series2.id}/episodes/1/watched')
    r = await client.get(f'/2/series/user-stats')
    assert r.status_code == 200
    data = schemas.User_series_stats.model_validate(r.json())
    assert data.episodes_watched == 5
    assert data.episodes_watched_minutes == 160
    assert data.series_watched == 2
    assert data.series_finished == 2


if __name__ == '__main__':
    run_file(__file__)