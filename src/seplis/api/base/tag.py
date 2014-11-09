import urllib.parse
import logging
from seplis import utils
from seplis.api import models, constants
from seplis.api.base.pagination import Pagination
from seplis.api.decorators import new_session
from seplis.api.connections import database

class Tag(object):

    def to_dict(self):
        return self.__dict__

    def cache(self):
        with database.redis.pipeline() as pipe:
            def c(name):
                for d in self.__dict__:
                    pipe.hset(name, d, self.__dict__[d])
            name = 'tags:{}'.format(self.id)
            [pipe.hset(name, d, self.__dict__[d]) for d in self.__dict__]
            name = 'tags:names:{}.{}'.format(            
                urllib.parse.quote(self.type), 
                urllib.parse.quote(self.name),
            )
            [pipe.hset(name, d, self.__dict__[d]) for d in self.__dict__]
            pipe.execute()

    @classmethod
    def _format_from_query(cls, query):
        if not query:
            return None
        if isinstance(query, dict):
            tag = cls()
            tag.__dict__.update({
                'id': int(query['id']),
                'type': query['type'],
                'name': query['name'],
            })
            return tag
        tag = cls()
        tag.id = query.id
        tag.type = query.type
        tag.name = query.name
        return tag

    @classmethod
    def get_by_name(cls, type_, name):
        '''
        
        :param type_: str        
        :param name: str
        :returns: `Tag()`
        '''
        name = name.lower()
        type_ = type_.lower()
        name = 'tags:names:{}.{}'.format(            
            urllib.parse.quote(type_), 
            urllib.parse.quote(name),
        )
        tag = database.redis.hgetall(name)
        return cls._format_from_query(tag)

    @classmethod
    def get(cls, id_):
        '''
             
        :param id_: int
        :returns: `Tag()`
        '''
        key = 'tags:{}'.format(id_)
        tag = database.redis.hgetall(key)
        return cls._format_from_query(tag)

    @classmethod
    def new(cls, type_, name):        
        '''

        :param type_: str        
        :param name: str
        :returns: `Tag()`
        '''
        with new_session() as session:
            tag = models.Tag(
                name=name.lower(),
                type=type_.lower(),
            )
            session.add(tag)
            session.commit()
            tag = cls._format_from_query(
                tag
            )
            tag.cache()
            return tag

class Tags(object):

    @classmethod
    def get(cls, ids):
        '''
        Resolves a list of ids returned from redis to the correct
        tag objects.

        :param ids: list of str b encoded
        :returns: list of `Tag()`
        '''
        tag_names = ['tags:{}'.format(id_) for id_ in ids]
        with database.redis.pipeline() as pipe:
            [pipe.hgetall(name) for name in tag_names]            
            tags = pipe.execute()
        if tags:
            tags = [
                Tag._format_from_query(tag)
                for tag in tags if tag
            ]
            return tags
        return []

    @classmethod
    def get_by_user_relation(cls, user_id, type_, relation_id):
        '''
        Returns a list of tags added to the `relation_id` with a specific `type_`.

        :param user_id: int
        :param type_: str
        :param relation_id: int
        :returns: list og `Tag()`
        '''
        name = 'users:{}:tag_relations:{}.{}'.format(
            user_id,
            urllib.parse.quote(type_.lower()),
            relation_id,
        )
        tag_ids = database.redis.zrange(name, 0, -1)
        if tag_ids:
            return cls.get(tag_ids)
        return []

class User_tag_relation(object):

    @classmethod
    def get_relation_data(cls, user_id, tag_type, order_field='title', 
        tag_id=None, page=1, per_page=constants.PER_PAGE):
        '''
        Returns a list of relation data for a specific tag type tagged by the user.

        Set `tag_id` to None to get all tagged data.

        :param user_id: int
        :param tag_type: str
        :param order_field: str
        :param tag_id: int
        :param page: int
        :param per_page: int
        :returns: `seplis.api.base.pagination.Pagination()`
        '''
        if not tag_id:
            name = 'users:{user_id}:tags:types:{type}:objects'.format(
                user_id=user_id, 
                type=tag_type,
            )
        else:
            name = 'users:{user_id}:tags:{id}:objects'.format(
                user_id=user_id, 
                id=tag_id,
            )
        with database.redis.pipeline() as pipe:
            pipe.sort(
                name=name,
                start=(page - 1) * per_page,
                num=per_page,
                by='{}:*->{}'.format(tag_type, order_field),
                get='{}:*:data'.format(tag_type),
                alpha=True,
            )
            pipe.scard(name)
            response = pipe.execute()
            data = [utils.json_loads(d) for d in response[0]]
            return Pagination(
                per_page=per_page,
                total=int(response[1]),
                records=data,
                page=page,
            )

    @classmethod
    def get_tags(cls, user_id, tag_type):
        '''
        :param user_id: int
        :param tag_type: str
        :returns: list of `Tag()`
        '''
        tag_ids = database.redis.sort(
            name='users:{user_id}:tags:types:{type}'.format(
                user_id=user_id, 
                type=tag_type,
            ),
            by='tags:*->name',
            alpha=True,
        )
        with database.redis.pipeline() as pipe:
            [pipe.hgetall('tags:{}'.format(id_)) for id_ in tag_ids]
            return [Tag._format_from_query(tag) for tag in pipe.execute()]

    @classmethod
    def cache(cls, pipe, user_id, tag_id, tag_type, relation_id):
        pipe.zadd('users:{user_id}:tag_relations:{type}.{relation_id}'.format(
            user_id=user_id,
            type=tag_type,
            relation_id=relation_id,
        ), tag_id, tag_id)
        pipe.sadd('users:{user_id}:tags:types:{type}'.format(
            user_id=user_id, 
            type=tag_type,
        ), tag_id)
        # all relations for a tag type
        pipe.sadd('users:{user_id}:tags:types:{type}:objects'.format(
            user_id=user_id, 
            type=tag_type
        ), relation_id)
        # all relations for a specific tag
        pipe.sadd('users:{user_id}:tags:{id}:objects'.format(
            user_id=user_id, 
            id=tag_id
        ), relation_id)

    @classmethod
    def set(cls, tag_type, tag_name, user_id, relation_id):
        '''

        :param tag_type: str
        :param tag_name: str
        :param user_id: int
        :param relation_id: int
        :returns: `Tag()`
        '''
        tag = Tag.get_by_name(
            type_=tag_type,
            name=tag_name,
        )
        if not tag:
            tag = Tag.new(
                type_=tag_type,
                name=tag_name,
            )
        with database.redis.pipeline() as pipe:
            cls.cache(
                pipe=pipe,
                user_id=user_id,
                tag_id=tag.id,
                tag_type=tag.type,
                relation_id=relation_id,
            )
            response = pipe.execute()
            result = response[0]
        if result == 1:
            with new_session() as session:
                tag_relation = models.Tag_relation(
                    user_id=user_id,
                    type=tag_type,
                    relation_id=relation_id,
                    tag_id=tag.id,
                )
                session.merge(tag_relation)
                session.commit()
        return tag

    @classmethod
    def delete(cls, tag_id, user_id, relation_id):
        '''

        :param tag_id: int
        :param user_id: int
        :param relation_id: int
        :returns: boolean
        '''
        tag = Tag.get(
            id_=tag_id,
        )
        if not tag:
            return False
        with new_session() as session:
            result = session.query(
                models.Tag_relation,
            ).filter(
                models.Tag_relation.user_id == user_id,
                models.Tag_relation.type == tag.type,
                models.Tag_relation.relation_id == relation_id,
                models.Tag_relation.tag_id == tag_id,
            ).delete()
            session.commit()
            with database.redis.pipeline() as pipe:
                pipe.zrem('users:{}:tag_relations:{}.{}'.format(
                    user_id,
                    tag.type,
                    relation_id,
                ), tag.id)            
                pipe.srem('users:{user_id}:tags:{id}:objects'.format(
                    user_id=user_id, 
                    id=tag.id
                ), relation_id)
                pipe.execute()
            with database.redis.pipeline() as pipe:
                pipe.exists('users:{user_id}:tags:{id}:objects'.format(
                    user_id=user_id, 
                    id=tag.id
                ))                
                pipe.exists('users:{}:tag_relations:{}.{}'.format(
                    user_id,
                    tag.type,
                    relation_id,
                ))
                checks = pipe.execute()
                if not checks[0]:
                    pipe.srem('users:{user_id}:tags:types:{type}'.format(
                        user_id=user_id, 
                        type=tag.type,
                    ), tag.id)
                if not checks[1]:# when the relation has no relations to any tags, delete it from the users all list 
                    pipe.srem('users:{user_id}:tags:types:{type}:objects'.format(
                        user_id=user_id, 
                        type=tag.type
                    ), relation_id)
                pipe.execute()
            return True

