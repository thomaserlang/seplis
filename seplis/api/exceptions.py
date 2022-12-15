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
            message=message or 'The requested item was not found',
            errors=None,
        )

class Forbidden(API_exception):

    def __init__(self, message=None):
        API_exception.__init__(self,
            status_code=403,
            code=501, 
            message=message or 'Forbidden',
            errors=None,
        )

class Wrong_password(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=401,
            code=999, 
            message='Wrong password',
            errors=None,
        )

class Wrong_email_or_password_exception(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=401,
            code=1000, 
            message='Wrong email and/or password',
            errors=None,
        )

class Validation_exception(API_exception):

    def __init__(self, errors):
        API_exception.__init__( 
            self,
            status_code=400,
            code=1001,
            message='One or more fields failed validation',
            errors=errors,
        )

class Parameter_restricted(API_exception):

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
            message='Unsupported grant_type "{}"'.format(grant_type),
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
            message='Unknown client_id: {}'.format(client_id),
        )

class OAuth_unauthorized_grant_type_level_request_exception(API_exception):

    def __init__(self, required_level, app_level):
        API_exception.__init__(
            self,
            status_code=403,
            code=1008,
            message='This app does not have authorization to make'
                    ' this type of grant type request, required level: {},'
                    ' your app\'s level: {}'.format(required_level, app_level),
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
            message='Not signed in',
        )

class Restricted_access_exception(API_exception):

    def __init__(self, user_level, required_level):
        API_exception.__init__(self,
            status_code=403,
            code=1010, 
            message='Your access level: {}, is not high enough'
                    ' for the required level: {}'.format(user_level, required_level),
            extra={
                'required_level': required_level,
                'user_level': user_level,
            }
        )

class User_episode_not_watched(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=1300, 
            message='You have not watched this episode',
        )

class Show_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1400,
            message='Unknown show',
        )

class Show_external_field_missing(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1401,
            message='Missing externals',
        )

class Show_importer_not_in_external(API_exception):

    def __init__(self, external_type):
        API_exception.__init__(
            self,
            status_code=400,
            code=1402,
            message='Importer "{}" must have a registered id in externals'.format(external_type),
            extra={
                'external_type': external_type,
            }
        )

class Show_external_duplicated(API_exception):

    def __init__(self, external_title, external_value, show):
        API_exception.__init__(
            self,
            status_code=400,
            code=1403,
            message='A show with external name: "{}" and id: "{}" does already exist'.format(
                external_title, 
                external_value,
            ),
            extra={
                'show': show,
                'external_title': external_title,
                'external_value': external_value,
            }
        )

class User_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1500,
            message='Unknown user',
        )

class User_email_duplicate(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1501,
            message='Email does already exist',
        )

class User_username_duplicate(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1502,
            message='Username does already exist',
        )

class User_show_subtitle_lang_not_found(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=404,
            code=1510,
            message='Unknown user, show or no default subtitle for this show',
        )

class Episode_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=1600,
            message='Unknown episode',
        )

class Elasticsearch_exception(API_exception):

    def __init__(self, status_code=400, extra=None, message=None):
        API_exception.__init__(
            self,
            status_code=status_code,
            code=1700,
            message=message or 'Search error',
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
            message='An image with the external name and id does already exist',
            extra=duplicate_image,
        )

class Image_unknown(API_exception):
    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2001,
            message='Unknown image',
        )

class Image_no_data(API_exception):
    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2003,
            message='No image data assigned. Please upload an image',
        )

class Image_wrong_size(API_exception):
    def __init__(self, aspect_ratio):
        API_exception.__init__(self,
            status_code=400,
            code=2004,
            message=f'The image aspect ratio must be: {aspect_ratio}',
        )    
        
class File_upload_no_files(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2100,
            message='Zero files was uploaded',
        )

class File_upload_unrecognized_image(API_exception):

    def __init__(self):
        API_exception.__init__(self,
            status_code=400,
            code=2101,
            message='Unrecognized image type. Please upload a JPG or PNG image',
        )

class Play_server_unknown(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=2200,
            message='Unknown play server',
        )

class Play_server_invite_invalid(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=2250,
            message='Invite id is invalid',
        )

class Play_server_invite_already_has_access(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=2251,
            message='The user does already have access to this play server',
        )

class Play_server_access_user_no_access(API_exception):

    def __init__(self):
        API_exception.__init__(
            self,
            status_code=400,
            code=2260,
            message='The user doesn\'t have access to this play server',
        )