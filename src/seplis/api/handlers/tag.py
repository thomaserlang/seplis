import seplis.api.handlers.base
from seplis.api.decorators import authenticated
from seplis.api.base.tag import User_tag_relation, Tags
from seplis.api import constants
from seplis import schemas

class Relation_handler(seplis.api.handlers.base.Handler):

    def initialize(self, type_):
        super(Relation_handler, self).initialize()
        self.type = type_

    @authenticated(0)
    def put(self, user_id, show_id):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        self.validate(schemas.User_tag_relation_schema)
        tag = User_tag_relation.set(
            tag_type=self.type,
            tag_name=self.request.body['name'],
            user_id=user_id,
            relation_id=show_id,
        )
        self.write_object(tag)

    @authenticated(0)
    def delete(self, user_id, tag_id, show_id):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        User_tag_relation.delete(
            tag_id=tag_id,
            user_id=user_id,
            relation_id=show_id,
        )

    @authenticated(0)
    def get(self, user_id, show_id):
        tags = Tags.get_by_user_relation(
            user_id=user_id,
            type_=self.type,
            relation_id=show_id,
        )
        self.write_object(tags)

class Relations_handler(seplis.api.handlers.base.Handler):

    def initialize(self, type_):
        super(Relations_handler, self).initialize()
        self.type = type_

    @authenticated(0)
    def get(self, user_id, tag_id=None):
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.per_page))
        self.write_object(
            User_tag_relation.get_relation_data(
                user_id=user_id,
                tag_type=self.type,
                tag_id=tag_id,
                page=page,
                per_page=per_page,
            )
        )

class User_types_handler(seplis.api.handlers.base.Handler):

    @authenticated(0)
    def get(self, user_id):
        types = self.get_arguments('type')
        self.write_object(
            {type_: User_tag_relation.get_tags(user_id, type_) for type_ in types}
        )