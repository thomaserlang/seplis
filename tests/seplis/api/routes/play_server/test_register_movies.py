import pytest
import sqlalchemy as sa
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models
from seplis.api.database import database


@pytest.mark.asyncio
async def test_play_server_register_movies(client: AsyncClient):
    user_id = await user_signin(client)

    play_server: schemas.Play_server = await models.Play_server.save(data=schemas.Play_server_create(
        name='Test play',
        url='http://example.net',
        secret='2'*20
    ), user_id=user_id)

    movie1: schemas.Movie = await models.Movie.save(data=schemas.Movie_create(
        title='Test movie 1',
    ))    
    movie2: schemas.Movie = await models.Movie.save(data=schemas.Movie_create(
        title='Test movie 1',
    ))

    r = await client.put(f'/2/play-servers/{play_server.id}/movies', json=[
        {'movie_id': movie1.id},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_movie))
        assert r.all()[0].movie_id == movie1.id

    r = await client.patch(f'/2/play-servers/{play_server.id}/movies', json=[
        {'movie_id': movie2.id},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_movie).where(
            models.Play_server_movie.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].movie_id == movie1.id
        assert r[1].movie_id == movie2.id


    r = await client.patch(f'/2/play-servers/{play_server.id}/movies', json=[
        {'movie_id': movie2.id},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_movie).where(
            models.Play_server_movie.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].movie_id == movie1.id
        assert r[1].movie_id == movie2.id

    r = await client.delete(f'/2/play-servers/{play_server.id}/movies/{movie1.id}', headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_movie).where(
            models.Play_server_movie.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].movie_id == movie2.id

    r = await client.put(f'/2/play-servers/{play_server.id}/movies', json=[], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_movie).where(
            models.Play_server_movie.play_server_id == play_server.id
        ))
        assert len(r.all()) == 0


if __name__ == '__main__':
    run_file(__file__)