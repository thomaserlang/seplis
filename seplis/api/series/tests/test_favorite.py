import pytest

from seplis.api.series import Series, SeriesCreate, SeriesFavorite, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
@pytest.mark.filterwarnings('ignore:Duplicate')
async def test_series_favorite(client: AsyncClient) -> None:
    await user_signin(client)

    series: Series = await save_series(
        SeriesCreate(
            title='Test series',
        ),
        series_id=None,
    )

    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = parse_obj_as(SeriesFavorite, r.json())
    assert not f.favorite
    assert f.created_at is None

    r = await client.put(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204

    # Test handling duplicate
    r = await client.put(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = parse_obj_as(SeriesFavorite, r.json())
    assert f.favorite
    assert f.created_at is not None

    r = await client.delete(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = parse_obj_as(SeriesFavorite, r.json())
    assert not f.favorite
    assert f.created_at is None


if __name__ == '__main__':
    run_file(__file__)
