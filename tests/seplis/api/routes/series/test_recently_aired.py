import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_user_series_watchlist(client: AsyncClient):
    await user_signin(client)
    dt = datetime.now(tz=timezone.utc)
    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=2)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ))
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ))
    series3: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 3',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ))

    r = await client.get('/2/series/recently-aired?user_watchlist=true')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_result[schemas.Series_and_episode].model_validate(r.json())
    assert len(data.items) == 0

    r = await client.put(f'/2/series/{series1.id}/watchlist')
    assert r.status_code == 204, r.content
    r = await client.put(f'/2/series/{series2.id}/watchlist')
    assert r.status_code == 204, r.content
    
    r = await client.get('/2/series/recently-aired?user_watchlist=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series_and_episode].model_validate(r.json())
    assert len(data.items) == 2
    assert data.items[0].series.title == 'Test series 2'
    assert data.items[0].episode.number == 1
    assert data.items[1].series.title == 'Test series'
    assert data.items[1].episode.number == 1

    r = await client.get('/2/series/recently-aired?user_watchlist=true&user_can_watch=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series_and_episode].model_validate(r.json())
    assert len(data.items) == 0


if __name__ == '__main__':
    run_file(__file__)