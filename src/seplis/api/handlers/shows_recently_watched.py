import logging
from . import base
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated, new_session, auto_session
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database

class Handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    def get(self, user_id):
        pass