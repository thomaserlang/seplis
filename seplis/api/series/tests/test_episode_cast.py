# test for episode cast route
import pytest

from seplis.api.page_cursor import PageCursor
from seplis.api.person import PersonCreate, save_person
from seplis.api.series import EpisodeCastPerson, EpisodeCreate, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_episode_cast(client: AsyncClient) -> None:
    await user_signin(client, ['series:edit'])

    series = await save_series(
        SeriesCreate(
            title='Test series',
            episodes=[
                EpisodeCreate(number=1, title='Test episode'),
            ],
        )
    )

    person = await save_person(
        PersonCreate(
            name='Test person',
        )
    )

    # add cast member
    r = await client.put(
        f'/2/series/{series.id}/episodes/1/cast',
        json={
            'person_id': person.id,
            'character': 'Test character',
        },
    )
    assert r.status_code == 204, r.content

    # add cast member again
    r = await client.put(
        f'/2/series/{series.id}/episodes/1/cast',
        json={
            'person_id': person.id,
            'character': 'Test character',
        },
    )
    assert r.status_code == 204

    # get cast members
    r = await client.get(f'/2/series/{series.id}/episodes/1/cast')
    assert r.status_code == 200
    cast = parse_obj_as(PageCursor[EpisodeCastPerson], r.json())
    assert len(cast.records) == 1
    assert cast.records[0].person.id == person.id
    assert cast.records[0].character == 'Test character'


if __name__ == '__main__':
    run_file(__file__)
