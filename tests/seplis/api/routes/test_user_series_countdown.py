import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from seplis import logger
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_user_series_following(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])
    dt = datetime.now(tz=timezone.utc)
    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ), series_id=None)
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ), series_id=None)

    r = await client.get('/2/users/me/series-recently-aired')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series_and_episode].parse_obj(r.json())
    assert data.total == 0

    r = await client.put(f'/2/series/{series1.id}/following')
    assert r.status_code == 204, r.content
    
    r = await client.get('/2/users/me/series-recently-aired')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series_and_episode].parse_obj(r.json())
    assert data.total == 1
    assert data.items[0].series.title == 'Test series'
    assert data.items[0].episode.number == 1


if __name__ == '__main__':
    run_file(__file__)