import pytest

from seplis.api.page_cursor import PageCursor
from seplis.api.series import Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_user_series_watchlist(client: AsyncClient) -> None:
    await user_signin(client)

    series1: Series = await save_series(
        SeriesCreate(
            title='Test series',
        ),
        series_id=None,
    )
    series2: Series = await save_series(
        SeriesCreate(
            title='Test series 2',
        ),
        series_id=None,
    )

    r = await client.put(f'/2/series/{series1.id}/watchlist')
    assert r.status_code == 204

    r = await client.get('/2/series?user_watchlist=true')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series1.id

    r = await client.put(f'/2/series/{series2.id}/watchlist')
    assert r.status_code == 204

    r = await client.get(
        '/2/series?user_watchlist=true&per_page=1&sort=user_watchlist_added_at_asc'
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series1.id

    r = await client.get(
        '/2/series',
        params={
            'user_watchlist': 'true',
            'cursor': data.cursor,
            'per_page': 1,
            'sort': 'user_watchlist_added_at_asc',
        },
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 1
    assert data.records[0].id == series2.id


if __name__ == '__main__':
    run_file(__file__)
