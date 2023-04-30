import pytest
from seplis.api import constants, schemas
from seplis.api.testbase import client, run_file, AsyncClient, user_signin

@pytest.mark.asyncio
async def test_person(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_SHOW)])

    # create person
    r = await client.post('/2/people', json={
        'name': 'Test person',
        'birthday': '1990-01-01',
        'externals': {
            'imdb': 'nm0000001',
        }
    })
    assert r.status_code == 201
    person = schemas.Person.parse_obj(r.json())

    # get person
    r = await client.get(f'/2/people/{person.id}')
    assert r.status_code == 200
    person = schemas.Person.parse_obj(r.json())
    assert person.name == 'Test person'
    assert person.externals['imdb'] == 'nm0000001'

    # update person
    r = await client.put(f'/2/people/{person.id}', json={
        'name': 'Test person 2',
        'externals': {
            'themoviedb': 123,
        }
    })
    assert r.status_code == 200

    # get person
    r = await client.get(f'/2/people/{person.id}')
    assert r.status_code == 200
    person = schemas.Person.parse_obj(r.json())
    assert person.name == 'Test person 2'
    assert person.externals['themoviedb'] == '123'
    assert 'imdb' not in person.externals

    # test updating a person with patch
    r = await client.patch(f'/2/people/{person.id}', json={
        'externals': {
            'imdb': 'nm0000001',
        }
    })
    assert r.status_code == 200
    person = schemas.Person.parse_obj(r.json())
    assert person.name == 'Test person 2'
    assert person.externals['themoviedb'] == '123'
    assert person.externals['imdb'] == 'nm0000001'


    # delete person
    r = await client.delete(f'/2/people/{person.id}')
    assert r.status_code == 204

    # get person
    r = await client.get(f'/2/people/{person.id}')
    assert r.status_code == 404


if __name__ == '__main__':
    run_file(__file__)
