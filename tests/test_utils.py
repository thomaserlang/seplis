import nose
from unittest import TestCase
from seplis import utils

class test_parse_link_header(TestCase):

    def test(self):
        header = '<https://api.example.com/1/users?page=2&per_page=1>; rel="next", <https://api.example.com/1/users?page=3&per_page=1>; rel="last"'
        parsed = utils.parse_link_header(header)
        self.assertEqual(parsed, {
            'next': 'https://api.example.com/1/users?page=2&per_page=1',
            'last': 'https://api.example.com/1/users?page=3&per_page=1'
        })

if __name__ == '__main__':
    nose.run(defaultTest=__name__)