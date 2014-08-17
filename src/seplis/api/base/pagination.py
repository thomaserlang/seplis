import math
from seplis import utils

class Pagination(object):

    def __init__(self, page, per_page, total, records):
        '''
        :param per_page:
            Specify the max number in records.
        :param total_records:
            The total number of records that the query
            would return if there were no limit.
        :param records: list
            A list of records.
        '''
        self.page = page
        self.total = total
        self.records = records
        self.pages = 0
        self.per_page = per_page
        if (per_page > 0) and total: 
            self.pages = int(math.ceil(float(total) / per_page))

    def links(self, uri, arguments):
        links = {}
        arguments['per_page'] = [self.per_page]
        if self.page > 1 and self.page <= self.pages:
            arguments['page'] = [1]
            links['first'] = '{}?{}'.format(uri, utils.url_encode_tornado_arguments(arguments))
            arguments['page'] = [self.page - 1]
            links['prev'] = '{}?{}'.format(uri, utils.url_encode_tornado_arguments(arguments))
        if self.page >= 1 and self.page < self.pages:
            arguments['page'] = [self.page + 1]
            links['next'] = '{}?{}'.format(uri, utils.url_encode_tornado_arguments(arguments))
        if self.page < self.pages and self.pages > 1:            
            arguments['page'] = [self.pages]
            links['last'] = '{}?{}'.format(uri, utils.url_encode_tornado_arguments(arguments))
        return links

    def links_header_format(self, uri, arguments):
        return ', '.join(['<{}>; rel="{}"'.format(urn, rel) for rel, urn in self.links(uri, arguments).items()])

    def to_dict(self):
        return self.__dict__