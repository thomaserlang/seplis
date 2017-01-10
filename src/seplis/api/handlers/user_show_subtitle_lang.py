import logging
import good
from seplis.api.decorators import authenticated, new_session
from seplis.api.handlers import base
from seplis.api import models, exceptions, constants
from seplis import schemas
from tornado import gen
from tornado.concurrent import run_on_executor


class Handler(base.Handler):

    __schema__ = good.Schema({
        'subtitle_lang': good.Maybe(good.All(
            good.Lower(), good.Length(min=1, max=20)
        )),
        'audio_lang': good.Maybe(good.All(
            good.Lower(), good.Length(min=1, max=20)
        ))
    }, default_keys=good.Optional)

    @authenticated(constants.LEVEL_USER)
    def get(self, user_id, show_id):
        self.check_user_edit(user_id)
        data = models.User_show_subtitle_lang.get(
            user_id=user_id,
            show_id=show_id,
        )
        if data:
            self.write_object(data)
        else:
            self.set_status(204)

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def put(self, user_id, show_id):
        self.check_user_edit(user_id)
        yield self._put(user_id, show_id)
        self.set_status(204)

    @run_on_executor
    def _put(self, user_id, show_id):
        data = self.validate()
        with new_session() as session:
            d = models.User_show_subtitle_lang(
                user_id=user_id,
                show_id=show_id,
                subtitle_lang=data.get('subtitle_lang', None),
                audio_lang=data.get('audio_lang', None),
            )
            session.merge(d)
            session.commit()

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def patch(self, user_id, show_id):
        self.check_user_edit(user_id)
        yield self._patch(user_id, show_id)
        self.set_status(204)

    @run_on_executor
    def _patch(self, user_id, show_id):
        data = self.validate()
        with new_session() as session:
            d = models.User_show_subtitle_lang(
                user_id=user_id,
                show_id=show_id,
            )
            if 'subtitle_lang' in data:
                d.subtitle_lang = data['subtitle_lang']
            if 'audio_lang' in data:
                d.audio_lang = data['audio_lang']
            session.merge(d)
            session.commit()