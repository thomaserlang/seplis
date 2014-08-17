import logging
from seplis.web.handlers import base
from tornado import gen

class Shows_handler(base.Handler_authenticated):

    @gen.coroutine
    def get(self, user_id):
        tag_id = int(self.get_argument('tag_id', 0))
        page = int(self.get_argument('page', 1))
        tags, shows = yield [
            self.client.get('/users/{}/tags?type=shows'.format(
                user_id,
            )),
            self.client.get(
                '/users/{}/tags/shows?page={}'.format(user_id, page) if not tag_id else '/users/{}/tags/{}/shows?page={}'.format(user_id, tag_id, page)
            ),
        ]
        url = self.reverse_url('user_tagged_shows', self.current_user['id'])
        self.render(
            'tagged_shows.html',
            title='Tagged shows- SEPLIS',
            tags=tags,
            shows=shows,
            selected_tag_id=tag_id,
            user_id=user_id,
            next_page='{}?tag_id={}&page={}'.format(url, tag_id, page+1) if page < shows['pages'] else '',
            prev_page='{}?tag_id={}&page={}'.format(url, tag_id, page-1) if page > 1 else '',
            total_results=shows['total_results'],
        )

class Relation_handler(base.Handler_authenticated):

    @gen.coroutine
    def get(self):
        tags = yield self.client.get('/users/{user_id}/tags/{type_}/{relation_id}'.format(
            user_id=self.current_user['id'],
            type_=self.get_argument('type'),
            relation_id=self.get_argument('relation_id'),
        ))
        self.write_object(tags)

    @gen.coroutine
    def post(self):
        method = self.get_argument('method')
        if method == 'add':
            tag = yield self.client.put(
                  '/users/{user_id}/tags/{type_}/{relation_id}'.format(
                    user_id=self.current_user['id'],
                    type_=self.get_argument('type'),
                    relation_id=self.get_argument('relation_id'),
                ),
                {
                    'name': self.get_argument('name'),
                }
            )
            self.write_object(tag)
        elif method == 'delete':
            yield self.client.delete(
                '/users/{user_id}/tags/{tag_id}/{type_}/{relation_id}'.format(
                    user_id=self.current_user['id'],
                    tag_id=self.get_argument('tag_id'),
                    type_=self.get_argument('type'),
                    relation_id=self.get_argument('relation_id'),
                )
            )