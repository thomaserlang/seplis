import logging, json
from seplis.api import exceptions
from seplis.api.handlers import base

class Handler(base.Handler):

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
                            'nested': { 
                                'path': 'titles',   
                                'query': {
                                    'bool': {
                                        'should': [
                                            {'multi_match': {
                                                'boost': 4,
                                                'query': args.query[0],
                                                'operator': 'and',
                                                'fields': [
                                                    'titles.title',
                                                    'titles.title._2gram',
                                                    'titles.title._3gram',
                                                ]
                                            }},
                                            {'multi_match': {
                                                'query': args.query[0],
                                                'type': 'bool_prefix',
                                                'minimum_should_match': '75%',
                                                'fields': [
                                                    'titles.title',
                                                    'titles.title._2gram',
                                                    'titles.title._3gram',
                                                ]
                                            }},
                                        ]
                                    }
                                }
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