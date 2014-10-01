import seplis.api.handlers.base
import logging
from seplis.decorators import new_session
from seplis.api import models
from seplis.schemas import App_schema
from datetime import datetime
from seplis.utils import random_key
from seplis.api.base.app import App
from seplis.api.decorators import authenticated
from seplis.api import exceptions 

class Handler(seplis.api.handlers.base.Handler):
    '''
    Handles app stuff...
    '''

    @authenticated(0)
    def post(self, app_id=None):
        if app_id:
            raise exceptions.Parameter_must_not_be_set_exception('app_id must not be set when creating a new app')
        App_schema(self.request.body)
        app = App.new(
            user_id=self.current_user.id,
            name=self.request.body['name'],
            redirect_uri=self.request.body['redirect_uri'],
            level=0,
        )
        self.set_status(201)
        self.write_object(app)

    @authenticated(0)
    def get(self, app_id=None):
        if not app_id:
            raise exceptions.Parameter_missing_exception('app_id parameter is missing')
        app = App.get(app_id)
        if not app:
            raise exceptions.Not_found('app with id: {} could not be found'.format(app_id))            
        self.write_object(app)