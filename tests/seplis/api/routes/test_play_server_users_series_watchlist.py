import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models, database


@pytest.mark.asyncio
async def test_get_play_servers_user_series_watchlist(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    play_server = schemas.Play_server.parse_obj(r.json())

    series = await models.Series.save(data=schemas.Series_create(title='Test', externals={'thetvdb': 1}))

    await models.Series_watchlist.add(series_id=series.id, user_id=user_id)

    r = await client.get(f'/2/play-servers/{play_server.id}/users-series-watchlist')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert data.items[0].id == series.id

    r = await client.get(f'/2/play-servers/{play_server.id}/users-series-watchlist?added_at_ge=2023-03-19T00:00:00')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert data.items[0].id == series.id

    r = await client.get(f'/2/play-servers/{play_server.id}/users-series-watchlist?added_at_le=2023-03-19T00:00:00')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 0

    
    r = await client.get(f'/2/play-servers/{play_server.id}/users-series-watchlist?response_format=sonarr')
    assert r.status_code == 200
    data = r.json()
    assert data[0]['TvdbId'] == 1


if __name__ == '__main__':
    run_file(__file__)