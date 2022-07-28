import asyncio
from tornado.web import RequestHandler

from seplis import utils
from seplis.play.connections import database

class Handler(RequestHandler):

    async def get(self):
        if hasattr(self.application, 'shutting_down') and self.application.shutting_down == True:
            self.set_header('Content-Type', 'text/plain')
            self.write('SHUTTING DOWN')
            self.set_status(503)
            return
        
        result = await asyncio.gather(
            self.db_check(),
        )
        self.set_header('Content-Type', 'application/json')
        self.write(utils.json_dumps(result))
        if any([r['error'] for r in result]):
            self.set_status(500)
        else:
            self.set_status(200)
        self.finish()

    async def db_check(self):
        r = {
            'error': False, 
            'message': 'OK', 
            'service': 'Database',
        }
        try:
            database.engine.execute('SELECT 1')
        except Exception as e:
            r['error'] = True 
            r['message'] = f'Error: {str(e)}'
        return r