from tornado import web

class Menu(web.UIModule):

    def render(self):
        return self.render_string(
            'menu.html'
        )

class Fan_button(web.UIModule):

    def render(self, show):
        return self.render_string(
            'fan_button.html',
            show=show,
        )

class Watched_button(web.UIModule):

    def render(self, show, episode):
        return self.render_string(
            'watched_button.html',
            show=show,
            episode=episode,
        )

class Show_header(web.UIModule):

    def render(self, show):
        return self.render_string(
            'show/show_header.html',
            show=show,
        )