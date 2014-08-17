from tornado import web

class Module(web.UIModule):

    def render(self, tag_type, relation_id, tags):
        return self.render_string(
            'tags.html',
            tag_type=tag_type,
            relation_id=relation_id,
            tags=tags,
        )