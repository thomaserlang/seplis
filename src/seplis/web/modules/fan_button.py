from tornado import web

class Module(web.UIModule):

    def render(self, show):
        return self.render_string(
            'fan_button.html',
            show=show,
        )