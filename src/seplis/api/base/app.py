from seplis.api.decorators import new_session
from seplis.api import models
from datetime import datetime
from seplis.utils import random_key

class App(object):

    def __init__(self, id_, user_id, name, redirect_uri, level, client_id, client_secret):
        '''

        :param id_: int
        :param user_id: int
            creator of the app
        :param name: str
        :param redirect_uri: str
        :param level: int
            1: read
            2: write
            3: system
        :param client_id: str
        :param client_secret: str
        '''
        self.id = id_
        self.user_id = user_id
        self.name = name
        self.redirect_uri = redirect_uri
        self.level = level
        self.client_id = client_id
        self.client_secret = client_secret

    def to_dict(self):
        return self.__dict__

    @classmethod
    def _format_from_query(cls, query):
        if not query:
            return None
        return cls(
            id_=query.id,
            user_id=query.user_id,
            name=query.name,
            redirect_uri=query.redirect_uri,
            level=query.level,
            client_id=query.client_id,
            client_secret=query.client_secret,
        )

    @classmethod
    def new(cls, user_id, name, redirect_uri, level):
        '''

        :param user_id: int
            creator of the app
        :param name: str
        :param redirect_uri: str
        :param level: int
            1: read
            2: write
            3: system
        :returns: `App()`
        '''
        with new_session() as session:
            app = models.App(
                user_id=user_id,
                name=name,
                client_id=random_key(),
                client_secret=random_key(),
                redirect_uri=redirect_uri,
                level=level,
                created=datetime.utcnow(),
            )
            session.add(app)
            session.commit()
            return cls._format_from_query(app)

    @classmethod
    def get(cls, id_):
        '''

        :param id_: int
        :returns: `App()`
        '''
        with new_session() as session:
            app = session.query(
                models.App,
            ).filter(
                models.App.id == id_,
            ).first()
            return cls._format_from_query(app)

    @classmethod
    def get_by_client_id(cls, client_id):
        '''

        :param client_id: str
        :returns: `App()`
        '''
        with new_session() as session:
            app = session.query(
                models.App,
            ).filter(
                models.App.client_id == client_id,
            ).first()
            return cls._format_from_query(app)