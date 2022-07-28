from unittest import TestCase
from seplis.api import models, exceptions
from seplis.utils.sqlalchemy import sort_parser
from sqlalchemy import asc, desc, sql

class Test_sort_parser(TestCase):

    def test(self):
        lookup = {
            'show_id': models.Show.id,
            'user': {
                'name': models.User.name,
            },
            'sub': {
                'subsub': {
                   'name': models.User.name, 
                }
            }
        }
        sort = sort_parser('show_id', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.asc_op)
        sort = sort_parser('show_id:desc', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.desc_op)

        self.assertRaises(
            exceptions.Sort_not_allowed,
            sort_parser,
            'show_id:desc, wrong', 
            lookup,
        )        

        self.assertRaises(
            exceptions.Sort_not_allowed,
            sort_parser,
            'episode', 
            lookup,
        )

        sort = sort_parser('user.name', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.asc_op)
        self.assertEqual(sort[0].element, models.User.name)

        sort = sort_parser('user.name:desc', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.desc_op)
        self.assertEqual(sort[0].element, models.User.name)

        sort = sort_parser('user.name, show_id:desc', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.asc_op)
        self.assertEqual(sort[0].element, models.User.name)
        self.assertEqual(sort[1].modifier, sql.operators.desc_op)
        self.assertEqual(sort[1].element, models.Show.id)

        sort = sort_parser('sub.subsub.name:asc', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.asc_op)
        self.assertEqual(sort[0].element, models.User.name)

        sort = sort_parser('sub.subsub.name:desc', lookup)
        self.assertEqual(sort[0].modifier, sql.operators.desc_op)
        self.assertEqual(sort[0].element, models.User.name)

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)