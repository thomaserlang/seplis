import pytest
import sqlalchemy as sa

from seplis.api.database import database
from seplis.api.movie import Movie, MovieCreate, save_movie
from seplis.api.play_server import (
    MPlayServerMovie,
    PlayServer,
    PlayServerCreate,
    save_play_server,
)
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
async def test_play_server_register_movies(client: AsyncClient) -> None:
    user_id = await user_signin(client)

    play_server: PlayServer = await save_play_server(
        data=PlayServerCreate(
            name='Test play', url='http://example.net', secret='2' * 32
        ),
        user_id=user_id,
    )

    movie1: Movie = await save_movie(
        data=MovieCreate(
            title='Test movie 1',
        )
    )
    movie2: Movie = await save_movie(
        data=MovieCreate(
            title='Test movie 1',
        )
    )

    # Invalid movie
    r = await client.put(
        f'/2/play-servers/{play_server.id}/movies',
        json=[
            {'movie_id': 0},
        ],
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 400, r.content

    r = await client.put(
        f'/2/play-servers/{play_server.id}/movies',
        json=[
            {'movie_id': movie1.id},
        ],
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(MPlayServerMovie))
        assert r.all()[0].movie_id == movie1.id

    r = await client.patch(
        f'/2/play-servers/{play_server.id}/movies',
        json=[
            {'movie_id': movie2.id},
        ],
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(
            sa.select(MPlayServerMovie).where(
                MPlayServerMovie.play_server_id == play_server.id
            )
        )
        r = r.all()
        assert r[0].movie_id == movie1.id
        assert r[1].movie_id == movie2.id

    r = await client.patch(
        f'/2/play-servers/{play_server.id}/movies',
        json=[
            {'movie_id': movie2.id},
        ],
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(
            sa.select(MPlayServerMovie).where(
                MPlayServerMovie.play_server_id == play_server.id
            )
        )
        r = r.all()
        assert r[0].movie_id == movie1.id
        assert r[1].movie_id == movie2.id

    r = await client.delete(
        f'/2/play-servers/{play_server.id}/movies/{movie1.id}',
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 204

    async with database.session() as session:
        r = await session.scalars(
            sa.select(MPlayServerMovie).where(
                MPlayServerMovie.play_server_id == play_server.id
            )
        )
        r = r.all()
        assert r[0].movie_id == movie2.id

    r = await client.put(
        f'/2/play-servers/{play_server.id}/movies',
        json=[],
        headers={
            'Authorization': f'Secret {"2" * 32}',
        },
    )
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(
            sa.select(MPlayServerMovie).where(
                MPlayServerMovie.play_server_id == play_server.id
            )
        )
        assert len(r.all()) == 0


if __name__ == '__main__':
    run_file(__file__)
