import pytest

from seplis.api.series import Series, SeriesCreate, SeriesUserRating, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_series_user_rating(client: AsyncClient) -> None:
    await user_signin(client)

    series: Series = await save_series(
        SeriesCreate(
            title='Test series',
        ),
        series_id=None,
    )

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = parse_obj_as(SeriesUserRating, r.json())
    assert data.rating is None

    r = await client.put(f'/2/series/{series.id}/user-rating', json={'rating': 5})
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = parse_obj_as(SeriesUserRating, r.json())
    assert data.rating == 5

    r = await client.put(f'/2/series/{series.id}/user-rating', json={'rating': 7})
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = parse_obj_as(SeriesUserRating, r.json())
    assert data.rating == 7

    r = await client.delete(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = parse_obj_as(SeriesUserRating, r.json())
    assert data.rating is None


if __name__ == '__main__':
    run_file(__file__)
