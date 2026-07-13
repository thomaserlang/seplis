from seplis.api.movie import MovieUpdate
from seplis.api.testbase import run_file
from seplis.utils.compare import compare


def test_compare() -> None:
    a = MovieUpdate(
        title='Test',
        plot='Some plot',
        genre_names=['Action', 'Drama'],
        language=None,
    )

    b = MovieUpdate(
        title='Test',
        plot='Some plot 2',
        genre_names=['Action'],
        language='en',
    )

    c = MovieUpdate(
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
