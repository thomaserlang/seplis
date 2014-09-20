from tornado.web import HTTPError

class API_exception(HTTPError):
    
    def __init__(self, status_code, code, message, errors=None, extra=None):
        '''
        :param status_code: int
            HTTP status code e.g. 400
        :param code: int
            internal error code
        :param message: str
        :param errors: list of error
        :param extra: object
            Extra information for the exception.
        '''
        HTTPError.__init__(self, status_code, message)
        self.status_code = status_code
        self.code = code
        self.errors = errors
        self.message = message
        self.extra = extra

class Not_found(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=404,
            code=500, 
            message='the requested item was not found',
            errors=None,
        )

class Wrong_email_or_password_exception(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=401,
            code=1000, 
            message='wrong email and/or password',
            errors=None,
        )

class Validation_exception(API_exception):

    def __init__(self, errors):
        API_exception.__init__( 
            self,
            status_code=400,
            code=1001,
            message='one or more fields failed validation',
            errors=errors,
        )

class Parameter_must_not_be_set_exception(API_exception):

    def __init__(self, message):
        API_exception.__init__(
            self,
            status_code=400,
            code=1002,
            message=message,
        )

class Parameter_missing_exception(API_exception):

    def __init__(self, message):
        API_exception.__init__(
            self,
            status_code=400,
            code=1003,
            message=message,
        )

class OAuth_unsuported_grant_type_exception(API_exception):

    def __init__(self, grant_type):
        API_exception.__init__(
            self,
            status_code=400,
            code=1006,
            message='unsupported grant_type "{}"'.format(grant_type),
            extra={
                'grant_type': grant_type,
            }
        )

class OAuth_unknown_client_id_exception(API_exception):

    def __init__(self, client_id):
        API_exception.__init__(
            self,
            status_code=400,
            code=1007,
            message='unknown client_id: {}'.format(client_id),
        )

class OAuth_unauthorized_grant_type_level_request_exception(API_exception):

    def __init__(self, required_level, app_level):
        API_exception.__init__(
            self,
            status_code=403,
            code=1008,
            message='this app does not have authorization to make this type of grant type request, required level: {}, your app\'s level: {}'.format(required_level, app_level),
            extra={
                'app_level': app_level,
                'required_level': required_level,
            }
        )

class Not_signed_in_exception(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=401,
            code=1009, 
            message='not signed in',
        )

class Restricted_access_exception(API_exception):

    def __init__(self, user_level, required_level):
        API_exception.__init__(self,
            status_code=403,
            code=1010, 
            message='your access level: {}, is not high enough for the required level: {}'.format(user_level, required_level),
            extra={
                'required_level': required_level,
                'user_level': user_level,
            }
        )

class Not_found_exception(API_exception):

    def __init__(self, message):
        API_exception.__init__(self,
            status_code=404,
            code=2000, 
            message=message,
        )

class User_not_following_show(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=3000, 
            message='you do not follow this show',
        )

class User_has_not_watched_this_episode(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=3001, 
            message='you have not watched this episode',
        )

class Show_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=4000,
            message='unknown show',
        )

class Show_external_field_must_be_specified_exception(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=4001,
            message='the external field must be specified before updating the index field',
        )

class Show_index_type_must_be_in_external_field_exception(API_exception):

    def __init__(self, external_type):
        API_exception.__init__(
            self,
            status_code=400,
            code=4002,
            message='Index type: "{}" must first be specified in the external field before adding it to the index field'.format(external_type),
            extra={
                'external_type': external_type,
            }
        )

class Show_external_duplicated(API_exception):

    def __init__(self, external_title, external_id, show):
        API_exception.__init__(
            self,
            status_code=400,
            code=4003,
            message='A show with the external name of: "{}" and id: "{}" does already exist'.format(external_title, external_id),
            extra={
                'show': show,
                'external_title': external_title,
                'external_id': external_id,
            }
        )

class User_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=5000,
            message='unknown user',
        )


class Episode_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=6000,
            message='unknown episode',
        )

class Elasticsearch_exception(API_exception):

    def __init__(self, status_code, extra):
        API_exception.__init__(
            self,
            status_code=status_code,
            code=7000,
            message='search error',
            extra=extra
        ) 

class Sort_not_allowed(API_exception):
    def __init__(self, sort):
        API_exception.__init__(self,
            status_code=400,
            code=8000,
            message='Sort by: "{}" is not allowed'.format(sort),
            extra=[sort],
        )

class Append_fields_not_allowed(API_exception):
    def __init__(self, fields):
        API_exception.__init__(self,
            status_code=400,
            code=9000,
            message='Append fields: "{}" are not allowed'.format(','.join(fields)),
            extra=[fields],
        )