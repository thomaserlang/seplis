from tornado import web

class Module(web.UIModule):

    def render(self):
        return self.render_string(
            'menu.html'
        )