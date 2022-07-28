import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
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


class modelTest(declarative_base()):
    __tablename__ = 'test'
    name = sa.Column(sa.String(50), primary_key=True)
    count = sa.Column(sa.Integer)
    created = sa.Column(sa.DateTime)

class test_redis_sa_model_dict(TestCase):

    def test(self):
        data = {
            'name': 'Thomas',
            'count': '1',
            'created': '2015-03-04T21:33:00Z',
        }
        utils.redis_sa_model_dict(
            data,
            modelTest,
        )
        self.assertEqual(data, {
            'name': 'Thomas',
            'count': 1,
            'created': '2015-03-04T21:33:00Z',
        })

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)