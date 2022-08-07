# coding=UTF-8
from unittest import TestCase
from datetime import date
from seplis.importer.shows.base import Series_importer_base

class test_show_importer_base(TestCase):

    pass

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)