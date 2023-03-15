from datetime import datetime
import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models, database


@pytest.mark.asyncio
async def test_get_play_server_series_following_missing_episodes(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    play_server = schemas.Play_server.parse_obj(r.json())

    series1 = await models.Series.save(data=schemas.Series_create(
        title='Test',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=datetime(2023, 3, 15, 0, 0, 0)),
        ]
    ), series_id=None)

    series2 = await models.Series.save(data=schemas.Series_create(
        title='Test 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=datetime(2023, 3, 14, 0, 0, 0)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=datetime(2023, 3, 15, 0, 0, 0)),
        ]
    ), series_id=None)

    series3 = await models.Series.save(data=schemas.Series_create(
        title='Test 3',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=datetime(2023, 3, 14, 0, 0, 0)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=datetime(2023, 3, 15, 0, 0, 0)),
        ]
    ), series_id=None)

    await models.Series_follower.follow(series_id=series1.id, user_id=user_id)
    await models.Series_follower.follow(series_id=series2.id, user_id=user_id)
    await models.Series_follower.follow(series_id=series3.id, user_id=user_id)
    await models.Play_server_episode.save(play_server_id=play_server.id, play_server_secret='a'*20, data=[
        schemas.Play_server_episode_create(
            series_id=series1.id,
            episode_number=1,
        ),
        schemas.Play_server_episode_create(
            series_id=series2.id,
            episode_number=2,
        ),
        schemas.Play_server_episode_create(
            series_id=series3.id,
            episode_number=2,
        ),
    ])

    r = await client.get(f'/2/play-servers/{play_server.id}/user-series-following-missing-episodes')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 2
    assert data.items[0].id == series2.id
    assert data.items[1].id == series3.id

    r = await client.get(f'/2/play-servers/{play_server.id}/user-series-following-missing-episodes?per_page=1')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert data.items[0].id == series2.id

    r = await client.get(f'/2/play-servers/{play_server.id}/user-series-following-missing-episodes', params={
        'per_page': 1,
        'cursor': data.cursor,
    })
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert data.items[0].id == series3.id
    

if __name__ == '__main__':
    run_file(__file__)