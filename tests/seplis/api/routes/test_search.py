import pytest
from seplis.api.testbase import client, run_file, AsyncClient, parse_obj_as
from seplis.api import schemas, models, elasticcreate
from seplis.api.database import database
from seplis import config

@pytest.mark.asyncio
async def test_search(client: AsyncClient):
    await elasticcreate.create_indices(database.es)

    movie1: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='National Treasure',
        externals={
            'imdb': 'tt0368891',
        },
        release_date='2004-11-19',
        alternative_titles=[
            'Nacionalno blago',
            'Büyük hazine',
        ],
    ), movie_id=None)
    
    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={ 'query': 'National Treasure'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id

    r = await client.get('/2/search', params={ 'title': 'National Treasure'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id

    r = await client.get('/2/search', params={ 'title': 'National Treasure', 'type': 'movie'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id

    r = await client.get('/2/search', params={ 'title': 'National Treasure', 'type': 'series'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 0

    r = await client.get('/2/search', params={ 'query': 'Natioal Treasure'})
    assert r.status_code == 200
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id


    r = await client.get('/2/search', params={ 'query': 'Natioal 2004'})
    assert r.status_code == 200
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id


    r = await client.get('/2/search', params={ 'query': 'Buyuk-hazine'})
    assert r.status_code == 200
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id


    r = await client.get('/2/search', params={ 'query': 'tt0368891'})
    assert r.status_code == 200
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == movie1.id

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='This is a test show',
        alternative_titles=[
            'kurt 1',
        ],
    ), series_id=None)

    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    # Test that lowercase does not matter
    r = await client.get('/2/search', params={'query': 'this'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1

    # Test that both title and alternative_titles is searched in
    r = await client.get('/2/search', params={'query': 'kurt'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1

    # Test ascii folding
    r = await client.get('/2/search', params={'query': 'kùrt'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1


    # Test apostrophe
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='DC\'s legend of something',
        alternative_titles=[
            'DC’s kurt',
        ],
        popularity=1,
    ), series_id=None)

    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={'query': 'dc\'s'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data
    assert data[0].id == series2.id
    r = await client.get('/2/search', params={'query': 'dc’s'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data
    assert data[0].id == series2.id
    r = await client.get('/2/search', params={'query': 'dcs'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data
    r = await client.get('/2/search', params={'query': '"dcs kurt"'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data
    assert data[0].id == series2.id
    r = await client.get('/2/search', params={'query': '"dc’s kurt"'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert data[0].id == series2.id
    r = await client.get('/2/search', params={'query': 'dc'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data

    # Test dotted search
    r = await client.get('/2/search', params={'query': 'dcs.legend.of.something'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data
    assert data[0].id == series2.id

    # Test score
    # Searching for "dcs legend of something" should not return
    # "Test DC's legend of something" as the first result

    series3: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test DCs legend of something',
    ), series_id=None)

    series4: schemas.Series = await models.Series.save(schemas.Series_create(
        title='legend',
    ), series_id=None)

    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={'title': 'dc\'s legend of something'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 2, data
    assert data[0].id == series2.id, data


    # Test the walking dead
    series5: schemas.Series = await models.Series.save(schemas.Series_create(
        title='The Walking Dead',
        premiered='2010-10-31',
    ), series_id=None)

    series6: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Fear the Walking Dead',
        premiered='2015-08-23',
    ), series_id=None)

    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={'title': 'The Walking Dead'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 2, data
    assert data[0].title == 'The Walking Dead'


    # Test `&` and `and`
    movie2: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Test & Test',
        release_date='2010-10-31',
    ), movie_id=None)
    
    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={'title': 'Test and Test'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 1, data


    await models.Series.save(schemas.Series_create(
        title='The Devil\'s Hour',
        alternative_titles=[
            'kurt 1',
        ],
        popularity=64.918,
    ), series_id=None)

    await models.Series.save(schemas.Series_create(
        title='Devils',
        popularity=14.16,
    ), series_id=None)

    await database.es.indices.refresh(index=config.data.api.elasticsearch.index_prefix+'titles')

    r = await client.get('/2/search', params={'title': 'Devil\'s'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 2, data
    assert data[0].title == 'Devils'

    r = await client.get('/2/search', params={'query': 'Devils'})
    assert r.status_code == 200, r.content
    data = parse_obj_as (list[schemas.Search_title_document], r.json())
    assert len(data) == 2, data
    assert data[0].title == 'Devils'


if __name__ == '__main__':
    run_file(__file__)