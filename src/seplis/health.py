from tornado.web import RequestHandler

class Handler(RequestHandler):

    async def get(self):
        self.set_header('Content-Type', 'text/plain')
        if hasattr(self.application, 'shutting_down') and self.application.shutting_down == True:
            self.write('SHUTTING DOWN')
            self.set_status(503)
            return
        self.set_status(200)
        self.write('READY')