from seplis.web.handlers import base

class Handler(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react.html')
