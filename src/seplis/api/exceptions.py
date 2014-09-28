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

    def __init__(self, message=None):
        API_exception.__init__(self,
            status_code=404,
            code=500, 
            message=message or 'the requested item was not found',
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
            code=1100, 
            message=message,
        )

class User_not_following_show(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=1200, 
            message='you do not follow this show',
        )

class User_has_not_watched_this_episode(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=1300, 
            message='you have not watched this episode',
        )

class Show_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=1400,
            message='unknown show',
        )

class Show_external_field_must_be_specified_exception(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1401,
            message='the external field must be specified before updating the index field',
        )

class Show_index_type_must_be_in_external_field_exception(API_exception):

    def __init__(self, external_type):
        API_exception.__init__(
            self,
            status_code=400,
            code=1402,
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
            code=1403,
            message='A show with the external name and id does already exist'.format(external_title, external_id),
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
            code=1500,
            message='unknown user',
        )


class Episode_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=1600,
            message='unknown episode',
        )

class Elasticsearch_exception(API_exception):

    def __init__(self, status_code, extra):
        API_exception.__init__(
            self,
            status_code=status_code,
            code=1700,
            message='search error',
            extra=extra
        ) 

class Sort_not_allowed(API_exception):
    def __init__(self, sort):
        API_exception.__init__(self,
            status_code=400,
            code=1800,
            message='Sort by: "{}" is not allowed'.format(sort),
            extra=[sort],
        )

class Append_fields_not_allowed(API_exception):
    def __init__(self, fields):
        API_exception.__init__(self,
            status_code=400,
            code=1900,
            message='Append fields: "{}" are not allowed'.format(','.join(fields)),
            extra=fields,
        )

class Image_external_duplicate(API_exception):    
    def __init__(self, duplicate_image):
        API_exception.__init__(self,
            status_code=400,
            code=2000,
            message='An image with the external name: {} and id: {} does already exist',
            extra=duplicate_image,
        )

class Image_unknown(API_exception):
    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2001,
            message='unknown image',
        )

class Image_set_wrong_type(API_exception):

    def __init__(self, image_type, needs_image_type):
        API_exception.__init__(self,
            status_code=400,
            code=2002,
            message='the image could not be set because of a wrong type',
            extra={
                'is': image_type,
                'needs': needs_image_type if isinstance(needs, list) \
                    else [needs_image_type],
            }
        )        
        
class File_upload_no_files(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2100,
            message='zero files was uploaded',
        )

class File_upload_unrecognized_image(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2101,
            message='unrecognized image type: please upload a JPG or PNG image',
        )