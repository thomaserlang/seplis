import logging
from . import base
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated, new_session, auto_session
from seplis.api.connections import database

class Handler(base.Handler):

    async def get(self, user_id):
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        pagination = models.Episode_watched.show_recently(
            user_id=int(user_id),
            per_page=per_page,
            page=page,
        )
        # fill with show and episode info.
        if pagination.records:
            show_ids = []
            episode_ids = []
            for w in pagination.records:
                show_ids.append(w['id'])
                episode_ids.append('{}-{}'.format(
                    w['id'],
                    w['user_watching']['episode_number'] if w['user_watching'] else 0
                ))
            show_docs = await self.es('/shows/show/_mget', body={
                'ids': show_ids,
            })
            episode_docs = await self.es('/episodes/episode/_mget', body={
                'ids': episode_ids,
            })
            episode_ids = []
            for w, show, episode in zip(
                pagination.records, 
                show_docs['docs'], 
                episode_docs['docs']
            ):
                if show['found']:
                    w.update(show['_source'])
                if episode['found']:
                    w['user_watching']['episode'] = episode['_source']
        self.write_object(pagination)