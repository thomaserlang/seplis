import pytest

from seplis.api.movie import MovieCastPerson, MovieCreate, save_movie
from seplis.api.page_cursor import PageCursor
from seplis.api.person import PersonCreate, save_person
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_movie_cast(client: AsyncClient) -> None:
    await user_signin(client, ['movie:edit'])

    movie = await save_movie(
        MovieCreate(
            title='Test movie',
        )
    )

    person = await save_person(
        PersonCreate(
            name='Test person',
        )
    )

    # add cast member
    r = await client.put(
        f'/2/movies/{movie.id}/cast',
        json={
            'person_id': person.id,
            'character': 'Test character',
        },
    )
    assert r.status_code == 204

    # add cast member again
    r = await client.put(
        f'/2/movies/{movie.id}/cast',
        json={
            'person_id': person.id,
            'character': 'Test character',
        },
    )
    assert r.status_code == 204

    # get cast members
    r = await client.get(f'/2/movies/{movie.id}/cast')
    assert r.status_code == 200
    cast = parse_obj_as(PageCursor[MovieCastPerson], r.json())
    assert len(cast.records) == 1
    assert cast.records[0].person.id == person.id
    assert cast.records[0].character == 'Test character'


if __name__ == '__main__':
    run_file(__file__)
