from seplis import logger
from seplis.api import schemas
from seplis.utils.compare import compare
from seplis.api.testbase import run_file


def test_compare():
    a = schemas.Movie_update(
        title='Test',
        plot='Some plot',
        genre_names=['Action', 'Drama'],
        language=None,
    )

    b = schemas.Movie_update(
        title='Test',
        plot='Some plot 2',
        genre_names=['Action'],
        language='en',     
    )

    c = schemas.Movie_update(
        title='Test',
        plot='Some plot',
        genre_names=['Drama', 'Action'],
        language=None,
    )

    d = compare(b, a)
    assert d['plot'] == 'Some plot 2'
    assert d['genre_names'] == ['Action']
    assert d['language'] == 'en'
    assert 'title' not in d

    d = compare(c, a)
    assert not d


if __name__ == '__main__':
    run_file(__file__)
