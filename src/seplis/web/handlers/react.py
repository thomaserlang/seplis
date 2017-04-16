from seplis.web.handlers import base

class Handler(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react.html')

class Handler_without_menu(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react_without_menu.html')

class Handler_without_menu_no_container(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react_without_menu_no_container.html')
