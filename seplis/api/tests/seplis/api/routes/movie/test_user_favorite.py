import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
async def test_movie_(client: AsyncClient) -> None:
    await user_signin(client)

    movie: schemas.Movie = await models.MMovie.save(schemas.Movie_create(
        title='Movie',
    ), movie_id=None)

    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200, r.content
    data = schemas.Movie_favorite.model_validate(r.json())
    assert not data.favorite
    assert data.created_at is None
    
    r = await client.put(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 204, r.content
    
    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200
    data = schemas.Movie_favorite.model_validate(r.json())
    assert data.favorite
    assert data.created_at is not None
    
    r = await client.delete(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200
    data = schemas.Movie_favorite.model_validate(r.json())
    assert not data.favorite
    assert data.created_at is None


if __name__ == '__main__':
    run_file(__file__)