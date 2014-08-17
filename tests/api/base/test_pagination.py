import nose
from unittest import TestCase
from seplis.api.base.pagination import Pagination

class test_pagination(TestCase):

    def test_links(self):
        p = Pagination(
            page=1,
            per_page=1,
            total=3,
            records=[1,2],
        )
        links = p.links('http://example.com', {'test': ['a', b'b']})
        self.assertTrue('last' in links)
        self.assertTrue('next' in links)  
        self.assertTrue('prev' not in links)
        self.assertTrue('first' not in links)
        
        p = Pagination(
            page=2,
            per_page=1,
            total=5,
            records=[1,2],
        )
        links = p.links('http://example.com', {})
        self.assertTrue('last' in links)
        self.assertTrue('next' in links)
        self.assertTrue('prev' in links)
        self.assertTrue('first' in links)        

        p = Pagination(
            page=5,
            per_page=1,
            total=5,
            records=[1,2],
        )
        links = p.links('http://example.com', {})
        self.assertTrue('last' not in links)
        self.assertTrue('next' not in links)
        self.assertTrue('prev' in links)
        self.assertTrue('first' in links)        

        p = Pagination(
            page=1,
            per_page=1,
            total=1,
            records=[1,2],
        )
        links = p.links('http://example.com', {})
        self.assertTrue('last' not in links)
        self.assertTrue('next' not in links)
        self.assertTrue('prev' not in links)
        self.assertTrue('first' not in links)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)