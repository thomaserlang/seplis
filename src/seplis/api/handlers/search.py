import logging, json
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
                        {                             
                            'bool': {
                                'should': [
                                    {
                                        'nested': {
                                            'path': 'titles',
                                            "score_mode": "max",
                                            'query': {
                                                'multi_match': {
                                                    'query': args.query[0],
                                                    'type': 'bool_prefix',
                                                    'fields': [
                                                        'titles.title',
                                                        'titles.title._2gram',
                                                        'titles.title._3gram',
                                                    ]
                                                }
                                            }
                                        }
                                    },
                                    {
                                        'match_phrase': {
                                            'title': {
                                                'query': args.query[0],
                                                'boost': 2,
                                            }
                                        },
                                    }
                                ]
                            }
                        },
                        { 'term': { 'imdb': args.query[0]} },
                    ]
                }
            }
        elif args.title:
            q = {
                'dis_max': {
                    'queries': [                        
                        {'nested': {
                            'path': 'titles',
                            'query': 
                                { 'match_phrase': { 'titles.title': args.title[0] }},
                        }},
                        { 'term': { 'imdb': args.title[0]} },
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