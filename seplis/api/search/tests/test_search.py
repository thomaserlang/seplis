from datetime import date

import pytest
from httpx import AsyncClient

from seplis.api.movie import MovieCreate, save_movie
from seplis.api.search.actions.search_mapping import normalize_name
from seplis.api.series import SeriesCreate, save_series

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query',
    [
        'National Treasure',
        'national trea',
        'Natioal Treasure',
        'National Treasuer',
        'Natioal 2004',
        'Buyuk-hazine',
        'Original name',
        'tt0368891',
    ],
)
async def test_query(client: AsyncClient, query: str) -> None:
    movie = await save_movie(
        MovieCreate(
            title='National Treasure',
            original_title='Original name',
            alternative_titles=['Büyük hazine'],
            release_date=date(2004, 11, 19),
            externals={'imdb': 'tt0368891'},
        )
    )
    response = await client.get('/2/search', params={'query': query})
    assert response.status_code == 200
    assert response.json()[0]['id'] == movie.id


@pytest.mark.parametrize(
    ('title', 'expected_year'),
    [
        ('Dune', 2021),
        ('Dune 1984', 1984),
        ('Dune (2021)', 2021),
        ('TT1160419', 2021),
        ('Dune (2020)', None),
        ('Duen (2021)', None),
        ('Dune Part', None),
        ('*** (2021)', None),
        ('*', None),
        (' ', None),
    ],
)
async def test_title(client: AsyncClient, title: str, expected_year: int | None) -> None:
    for year in (1984, 2021):
        await save_movie(
            MovieCreate(
                title='Dune',
                release_date=date(year, 1, 1),
                popularity=year,
                externals={'imdb': 'tt1160419'} if year == 2021 else {},
            )
        )
    await save_movie(MovieCreate(title='Dune: Part Two', popularity=10000))
    response = await client.get('/2/search', params={'title': title, 'type': 'movie'})
    assert response.status_code == 200
    data = response.json()
    assert (int(data[0]['release_date'][:4]) if data else None) == expected_year


@pytest.mark.parametrize('mode', ['query', 'title'])
async def test_type_filter(client: AsyncClient, mode: str) -> None:
    await save_movie(
        MovieCreate(title='National Treasure', externals={'imdb': 'tt0368891'})
    )
    for value in ('National Treasure', 'tt0368891'):
        response = await client.get('/2/search', params={mode: value, 'type': 'series'})
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.parametrize('mode', ['query', 'title'])
@pytest.mark.parametrize(
    ('stored', 'value'),
    [
        ("DC's Legends", 'dc’s legends'),
        ('Euphoria U.S', 'Euphoria US'),
        ('Test & Test', 'Test and Test'),
    ],
)
async def test_punctuation(
    client: AsyncClient, mode: str, stored: str, value: str
) -> None:
    series = await save_series(SeriesCreate(title=stored))
    response = await client.get('/2/search', params={mode: value})
    assert response.status_code == 200
    assert response.json()[0]['id'] == series.id


@pytest.mark.parametrize('mode', ['query', 'title'])
async def test_exact_title_before_popularity(client: AsyncClient, mode: str) -> None:
    series = await save_series(SeriesCreate(title='The Walking Dead'))
    await save_series(SeriesCreate(title='Fear the Walking Dead', popularity=1000))
    response = await client.get('/2/search', params={mode: 'The Walking Dead'})
    assert response.status_code == 200
    assert response.json()[0]['id'] == series.id
    if mode == 'title':
        assert len(response.json()) == 1


@pytest.mark.parametrize(
    ('query', 'literal', 'completion'),
    [
        ('ment', 'Ment', 'The Mentalist'),
        ('mental', 'Mental', 'The Mentalist'),
        ('brea', 'La Brea', 'Breaking Bad'),
        ('game', 'Game', 'Game of Thrones'),
        ('off', 'Off Ice', 'The Office'),
        ('dex', 'Dex', 'Dexter'),
        ('stranger', 'Stranger', 'Stranger Things'),
        ('sever', 'Sever', 'Severance'),
    ],
)
async def test_popular_completions(
    client: AsyncClient, query: str, literal: str, completion: str
) -> None:
    await save_series(SeriesCreate(title=literal, popularity=2, rating_votes=1000000))
    series = await save_series(
        SeriesCreate(title=completion, popularity=100, rating_votes=0)
    )
    for limit in (1, 25, 100):
        response = await client.get('/2/search', params={'query': query, 'limit': limit})
        assert response.status_code == 200
        assert response.json()[0]['id'] == series.id


@pytest.mark.parametrize('competitor', ['Coast', 'To Ast'])
async def test_popularity_does_not_force_fuzzy_matches(
    client: AsyncClient, competitor: str
) -> None:
    movie = await save_movie(MovieCreate(title='Toast', popularity=1))
    await save_movie(MovieCreate(title=competitor, popularity=1000))
    response = await client.get('/2/search', params={'query': 'toast'})
    assert response.status_code == 200
    assert response.json()[0]['id'] == movie.id


async def test_completion_match_quality_before_popularity(client: AsyncClient) -> None:
    jag = await save_series(
        SeriesCreate(
            title='JAG', alternative_titles=['JAG: Justicia Militar'], popularity=175.3048
        )
    )
    young_justice = await save_series(
        SeriesCreate(title='Young Justice', popularity=100.2714)
    )
    justified = await save_series(SeriesCreate(title='Justified', popularity=54.7065))
    just_shoot_me = await save_series(
        SeriesCreate(title='Just Shoot Me!', popularity=42.4039)
    )
    for limit in (1, 25, 100):
        response = await client.get('/2/search', params={'query': 'just', 'limit': limit})
        assert response.status_code == 200
        assert [d['id'] for d in response.json()] == [
            justified.id,
            just_shoot_me.id,
            young_justice.id,
            jag.id,
        ][:limit]
    response = await client.get('/2/search', params={'query': 'justicia militar'})
    assert response.json()[0]['id'] == jag.id


@pytest.mark.parametrize(
    ('query', 'title', 'other'),
    [
        ('ment', 'The Mentalist', 'Mental'),
        ('clock', 'A Clockwork Orange', 'Clock'),
        ('amer', 'An American Werewolf in London', 'American'),
    ],
)
async def test_completion_ignores_leading_articles(
    client: AsyncClient, query: str, title: str, other: str
) -> None:
    movie = await save_movie(MovieCreate(title=title, popularity=100))
    await save_movie(MovieCreate(title=other, popularity=1))
    response = await client.get('/2/search', params={'query': query})
    assert response.status_code == 200
    assert response.json()[0]['id'] == movie.id


async def test_completion_popularity_updates_and_identification(
    client: AsyncClient,
) -> None:
    ment = await save_series(
        SeriesCreate(title='Ment', popularity=2, premiered=date(2012, 9, 10))
    )
    mentalist = await save_series(SeriesCreate(title='The Mentalist', popularity=100))
    response = await client.get('/2/search', params={'query': 'ment'})
    assert response.json()[0]['id'] == mentalist.id
    for title in ('Ment', 'Ment (2012)'):
        response = await client.get('/2/search', params={'title': title})
        assert [d['id'] for d in response.json()] == [ment.id]
    await save_series({'popularity': 200}, series_id=ment.id)
    response = await client.get('/2/search', params={'query': 'ment'})
    assert response.json()[0]['id'] == ment.id


@pytest.mark.parametrize(
    ('mode', 'value'),
    [
        ('title', 'Blade Runner 2049'),
        ('title', 'Blade.Runner.2049'),
        ('title', 'Blade Runner 2049 (2017)'),
        ('query', 'blade runner 2049'),
        ('query', 'blade runer 2049'),
        ('query', 'blade runner (2017)'),
    ],
)
async def test_title_with_year_in_name(
    client: AsyncClient, mode: str, value: str
) -> None:
    movie = await save_movie(
        MovieCreate(
            title='Blade Runner 2049',
            release_date=date(2017, 1, 1),
        )
    )
    response = await client.get('/2/search', params={mode: value})
    assert response.status_code == 200
    assert response.json()[0]['id'] == movie.id


@pytest.mark.parametrize(
    ('title', 'found'),
    [
        ('1917', True),
        ('1917 (2019)', True),
        ('1917 (1917)', False),
    ],
)
async def test_numeric_title(client: AsyncClient, title: str, found: bool) -> None:
    await save_movie(MovieCreate(title='1917', release_date=date(2019, 1, 1)))
    response = await client.get('/2/search', params={'title': title})
    assert response.status_code == 200
    assert bool(response.json()) == found


@pytest.mark.parametrize('mode', ['query', 'title'])
@pytest.mark.parametrize('value', ['24', '24 2001', '24 (2001)', 'tt0285331'])
async def test_24(client: AsyncClient, mode: str, value: str) -> None:
    series = await save_series(
        SeriesCreate(
            title='24',
            premiered=date(2001, 11, 6),
            externals={'imdb': 'tt0285331'},
            alternative_titles=['24: Live Another Day', 'Twenty Four'],
            popularity=177.9875,
        )
    )
    await save_movie(MovieCreate(title='24', popularity=10))
    await save_series(SeriesCreate(title='24: Legacy', popularity=12.6541))
    for title in ('4-3-2-1 Hot and Sweet', '2 Hip 4 TV', '25'):
        await save_series(SeriesCreate(title=title, popularity=1000))
    for title_type in (None, 'series'):
        params = {mode: value}
        if title_type:
            params['type'] = title_type
        response = await client.get('/2/search', params=params)
        assert response.status_code == 200
        assert response.json()[0]['type'] == 'series'
        assert response.json()[0]['id'] == series.id
        assert response.json()[0]['imdb'] == 'tt0285331'


async def test_normalization() -> None:
    assert normalize_name('Büyük & Hazine') == 'buyuk and hazine'
    assert normalize_name('\u304c') != normalize_name('\u304b')
    assert normalize_name('***') == ''
