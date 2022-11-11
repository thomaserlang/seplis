import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from seplis import logger
from datetime import datetime, timezone, timedelta
from pydantic import parse_obj_as

@pytest.mark.asyncio
async def test_series_user_stats(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_USER)])
    
    air_dates = [
        datetime.now(tz=timezone.utc),
        (datetime.now(tz=timezone.utc) + timedelta(days=8)),
        (datetime.now(tz=timezone.utc) + timedelta(days=1)),
    ]
    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, season=1, episode=1, air_datetime=air_dates[0]),
            schemas.Episode_create(title='Episode 2', number=2, season=1, episode=2, air_datetime=air_dates[1]),
        ]
    ), series_id=None)

    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, season=1, episode=1, air_datetime=air_dates[0]),
            schemas.Episode_create(title='Episode 2', number=2, season=2, episode=2, air_datetime=air_dates[2]),
        ]
    ), series_id=None)

    # User must follow the series
    r = await client.get('/2/users/me/air-dates')
    assert r.status_code == 200
    data = parse_obj_as(list[schemas.Series_air_dates], r.json())
    assert len(data) == 0

    r = await client.put(f'/2/series/{series1.id}/following')
    assert r.status_code == 204
    
    r = await client.get('/2/users/me/air-dates')
    assert r.status_code == 200
    data = parse_obj_as(list[schemas.Series_air_dates], r.json())
    assert len(data) == 1
    assert data[0].air_date == air_dates[0].date()
    assert data[0].series[0].id == series1.id
    assert data[0].series[0].episodes[0].number == 1

    r = await client.put(f'/2/series/{series2.id}/following')
    assert r.status_code == 204

    r = await client.get('/2/users/me/air-dates')
    assert r.status_code == 200
    data = parse_obj_as(list[schemas.Series_air_dates], r.json())
    assert len(data) == 2
    assert data[0].air_date == air_dates[0].date()
    assert data[0].series[0].id == series1.id
    assert data[0].series[0].episodes[0].number == 1
    assert data[0].series[1].id == series2.id
    assert data[0].series[1].episodes[0].number == 1
    assert data[1].air_date == air_dates[2].date()
    assert data[1].series[0].id == series2.id
    assert data[1].series[0].episodes[0].number == 2


if __name__ == '__main__':
    run_file(__file__)