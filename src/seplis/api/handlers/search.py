from seplis.api import exceptions
from seplis.api.handlers import base
from seplis.api.schemas import Search_schema

class Handler(base.Handler):
    __arguments_schema__ = Search_schema

    async def get(self):
        query = self.build_query()
        if not query:
            raise exceptions.Elasticsearch_exception(message='No query')
        r = await self.es_async.search(index='titles', query=query)
        results = []
        for a in r['hits']['hits']:
            a['_source'].pop('titles')
            results.append(a['_source'])
        self.write_object(results)

    def build_query(self):
        args: Search_schema = self.validate_arguments()

        if args.query:
            q = {
                'dis_max': {
                    'queries': [
                        {'multi_match': {
                            'query': args.query[0],
                            'type': 'bool_prefix',
                            'fields': [
                                'titles^3',
                                'titles._2gram',
                            ]
                        }},
                        { 'term': { 'imdb': args.query[0]} },
                    ]
                }
            }
        elif args.title:
            q = {
                'multi_match': {
                    'query': args.title[0],
                    'operator': 'and',
                    'type': 'best_fields',
                    'fields': [
                        'titles',
                        'imdb',
                    ]
                }
            }

        if q and args.type:
            q = {
                'bool': {
                    'must': q,
                    'filter': {
                        'term': {
                            'type': args.type[0],
                        }
                    }
                }
            }
        
        return q