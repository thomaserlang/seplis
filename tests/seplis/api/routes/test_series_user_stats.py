import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_series_user_stats(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
            schemas.Episode_create(number=3, title='3', runtime=40),
        ]
    ), series_id=None)

    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code == 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 0
    assert data.episodes_watched_minutes == 0

    # watched time
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 1, data
    assert data.episodes_watched_minutes == 30, data

    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 2, data
    assert data.episodes_watched_minutes == 60, data

    r = await client.post(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 3, data
    assert data.episodes_watched_minutes == 90, data

    r = await client.post(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 4, data
    assert data.episodes_watched_minutes == 130, data


if __name__ == '__main__':
    run_file(__file__)