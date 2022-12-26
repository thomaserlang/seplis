import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models, database


@pytest.mark.asyncio
async def test_play_server(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    play_server = schemas.Play_server.parse_obj(r.json())

    series = await models.Series.save(data=schemas.Series_create(
        title='Test',
    ), series_id=None)

    async with database.database.session() as session:
        await models.Series_follower.follow(series_id=series.id, user_id=user_id, session=session)
        await session.commit()

    r = await client.get(f'/2/play-servers/{play_server.id}/user-series-following')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series].parse_obj(r.json())
    assert data.items[0].id == series.id


if __name__ == '__main__':
    run_file(__file__)