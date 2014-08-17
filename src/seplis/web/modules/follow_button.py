from tornado import web

class Module(web.UIModule):

    def render(self, show):
        return self.render_string(
            'follow_button.html',
            show=show,
        )