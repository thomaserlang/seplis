import seplis.api.handlers.base
import logging
from seplis.api.decorators import authenticated, new_session
from seplis.api import models, exceptions
from seplis import schemas
from tornado import gen
from tornado.concurrent import run_on_executor

class Handler(seplis.api.handlers.base.Handler):
    '''
    Handles app stuff...
    '''

    @authenticated(0)
    @gen.coroutine
    def post(self, app_id=None):
        if app_id:
            raise exceptions.Parameter_restricted(
                'app_id must not be set when creating a new app'
            )
        app = yield self.create()
        self.set_status(201)
        self.write_object(app)

    @run_on_executor
    def create(self):
        data = self.validate(schemas.App_schema)
        with new_session() as session:
            app = models.App(
                user_id=self.current_user.id,
                name=data['name'],
                level=0,
                redirect_uri=data['redirect_uri'],
            )
            session.add(app)
            session.commit()
            return app.serialize()

    @authenticated(0)
    def get(self, app_id=None):
        if not app_id:
            raise exceptions.Parameter_missing_exception(
                'app_id parameter is missing'
            )
        app = models.App.get(app_id)
        if not app:
            raise exceptions.Not_found(
                'app with id: {} could not be found'.format(app_id)
            )            
        self.write_object(app)