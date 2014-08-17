from seplis.web.handlers import base
from tornado.web import authenticated

class Handler(base.Handler_authenticated):

    @authenticated
    def get(self):
        self.render(
            'settings.html',
            title='Settings - SEPLIS',
        )