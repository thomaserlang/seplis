import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_user_watched(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 1',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
            schemas.Episode_create(title='Episode 2', number=2),
        ]
    ), series_id=None)

    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1),
            schemas.Episode_create(title='Episode 2', number=2),
        ]
    ), series_id=None)


    movie1: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie 1',
    ), movie_id=None)


    movie2: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie 2',
    ), movie_id=None)


    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/movies/{movie1.id}/watched')
    assert r.status_code == 200, r.body

    r = await client.post(f'/2/movies/{movie2.id}/watched')
    assert r.status_code == 200, r.body


    r = await client.get(f'/2/users/me/watched')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.User_watched].parse_obj(r.json())
    assert len(data.items) == 4


    r = await client.get(f'/2/users/me/watched?user_can_watch=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.User_watched].parse_obj(r.json())
    assert len(data.items) == 0


if __name__ == '__main__':
    run_file(__file__)