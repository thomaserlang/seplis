import good
import logging
import tornado.escape
from .. import base
from tornado.gen import coroutine

class API_handler(base.API_handler):
    
    __arguments_schema__ = good.Schema({
        'q': good.All(good.Length(max=1), [str]),
        'sort': good.All(good.Length(max=1), [str]),
    }, default_keys=good.Optional)

    @coroutine
    def get(self, show_id):
        args = self.validate_arguments()
        episodes = yield self.client.get(
            '/shows/{}/episodes'.format(show_id), {
                'q': args.get('q', ''),
                'sort': args.get('sort', 'number:asc'),
                'per_page': 100,
            },
            all_=True,
        )
        self.write({'episodes': episodes})