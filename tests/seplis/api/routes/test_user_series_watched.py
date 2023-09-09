import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_user_series_watched(client: AsyncClient):
    await user_signin(client)

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

    r = await client.get('/2/series?user_has_watched=true&expand=user_last_episode_watched')
    assert r.status_code == 200
    data = schemas.Page_cursor_total_result[schemas.Series].model_validate(r.json())
    assert data.items == []

    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    
    r = await client.get('/2/series?user_has_watched=true&expand=user_last_episode_watched')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_total_result[schemas.Series].model_validate(r.json())
    assert data.items[0].id == series1.id
    assert data.items[0].user_last_episode_watched.number == 1

    
    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.get('/2/series?user_has_watched=true&expand=user_last_episode_watched')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_total_result[schemas.Series].model_validate(r.json())
    assert len(data.items) == 2
    assert data.items[0].id == series1.id
    assert data.items[0].user_last_episode_watched.number == 1
    assert data.items[1].id == series2.id
    assert data.items[1].user_last_episode_watched.number == 2


if __name__ == '__main__':
    run_file(__file__)