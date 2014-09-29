from tornado import web

class Fan_module(web.UIModule):

    def render(self, show):
        return self.render_string(
            'fan_button.html',
            show=show,
        )

class Watched_module(web.UIModule):

    def render(self, show, episode):
        return self.render_string(
            'watched_button.html',
            show=show,
            episode=episode,
        )