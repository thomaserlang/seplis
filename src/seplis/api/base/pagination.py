import math
from seplis import utils
from sqlalchemy import func

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

    @classmethod
    def from_query(cls, query, count_field, page, per_page):
        '''
        Counts the total records.
        Returns a `Pagination()` object with page, per_page, total
        prefilled. Fill records afterwards.

        Example:

            query = session.query(
                models.Shows,
            ).filter(
                models.Show_fan.user_id == user_id,
                models.Show.id == models.Show_fan.show_id,
            )
            pagination = Pagination.from_query(
                query,
                count_field=models.Show_fan.show_id,
                page=page,
                per_page=per_page,
            )
            query = query.limit(
                int(per_page),
            ).offset(
                int(page-1) * int(per_page),
            )
            rows = query.all()
            shows = []
            for show in rows:
                shows.append(
                    Show._format_from_row(show)
                )
            pagination.records = shows
            return pagination


        :param query: SQLAlchemy query
        :param count_field: The SQLalchemy field that should be used count
                            the total number of results.
        :param page: int
        :param per_page: int
        '''
        total = query.with_entities(
            func.count(
                count_field
            ).label('count')
        ).first()
        return cls(
            page=page,
            per_page=per_page,
            total=total.count,
            records=None,
        )