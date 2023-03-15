import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_user_series_favorites(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
    ), series_id=None)
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
    ), series_id=None)

    r = await client.put(f'/2/series/{series1.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/series?user_favorites=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_total_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series1.id

    r = await client.put(f'/2/series/{series2.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/series?user_favorites=true&per_page=1&sort=user_favorite_added_at_asc')
    assert r.status_code == 200, r.content
    data = schemas.Page_cursor_total_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series1.id

    r = await client.get(f'/2/series?user_favorites=true', params={
        'cursor': data.cursor,
        'per_page': 1,
        'sort': 'user_favorite_added_at_asc',
    })
    assert r.status_code == 200
    data = schemas.Page_cursor_total_result[schemas.Series].parse_obj(r.json())
    assert len(data.items) == 1
    assert data.items[0].id == series2.id


if __name__ == '__main__':
    run_file(__file__)