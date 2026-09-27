from typing import Any


class APIException(Exception):
    def __init__(
        self,
        status_code: int,
        code: int,
        message: str,
        errors: Any = None,
        extra: Any = None,
    ) -> None:
        """
        :param status_code: int
            HTTP status code e.g. 400
        :param code: int
            internal error code
        :param message: str
        :param errors: list of error
        :param extra: object
            Extra information for the exception.
        """
        self.status_code = status_code
        self.code = code
        self.errors = errors
        self.message = message
        self.extra = extra


class NotFound(APIException):
    def __init__(self, message: str | None = None) -> None:
        APIException.__init__(
            self,
            status_code=404,
            code=500,
            message=message or 'The requested item was not found',
            errors=None,
        )


class Forbidden(APIException):
    def __init__(self, message: str | None = None) -> None:
        APIException.__init__(
            self,
            status_code=403,
            code=501,
            message=message or 'Forbidden',
            errors=None,
        )


class WrongPassword(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=999,
            message='Wrong password',
            errors=None,
        )


class WrongLoginOrPassword(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1000,
            message='Wrong login and/or password',
            errors=None,
        )


class ValidationException(APIException):
    def __init__(self, errors: Any) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1001,
            message='One or more fields failed validation',
            errors=errors,
        )


class ParameterRestricted(APIException):
    def __init__(self, message: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1002,
            message=message,
        )


class ParameterMissingException(APIException):
    def __init__(self, message: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1003,
            message=message,
        )


class OauthUnsupportedGrantTypeException(APIException):
    def __init__(self, grant_type: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1006,
            message=f'Unsupported grant_type "{grant_type}"',
            extra={
                'grant_type': grant_type,
            },
        )


class OauthUnknownClientIdException(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1007,
            message='Unknown client_id',
        )


class OauthUnauthorizedGrantTypeLevelRequestException(APIException):
    def __init__(self, required_level: int, app_level: int) -> None:
        APIException.__init__(
            self,
            status_code=403,
            code=1008,
            message='This app does not have authorization to make'
            f' this type of grant type request, required level: {required_level},'
            f" your app's level: {app_level}",
            extra={
                'app_level': app_level,
                'required_level': required_level,
            },
        )


class NotSignedInException(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=401,
            code=1009,
            message='Not signed in',
        )


class RestrictedAccessException(APIException):
    def __init__(self, user_level: int, required_level: int) -> None:
        APIException.__init__(
            self,
            status_code=403,
            code=1010,
            message=f'Your access level: {user_level}, is not high enough'
            f' for the required level: {required_level}',
            extra={
                'required_level': required_level,
                'user_level': user_level,
            },
        )


class UserEpisodeNotWatched(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1300,
            message='You have not watched this episode',
        )


class SeriesUnknown(APIException):
    def __init__(self, series_id: int) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1400,
            message=f'Unknown series ({series_id})',
        )


class SeriesExternalDuplicated(APIException):
    def __init__(self, external_title: str, external_value: str, series: Any) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1403,
            message=(
                f'A series with external name: "{external_title}" and id: '
                f'"{external_value}" does already exist'
            ),
            extra={
                'series': series,
                'external_title': external_title,
                'external_value': external_value,
            },
        )


class UserUnknown(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1500,
            message='Unknown user',
        )


class UserEmailDuplicate(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1501,
            message='This email has already been used',
        )


class UserUsernameDuplicate(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1502,
            message='This username is taken',
        )


class DeviceAuthorizationUnknown(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=404,
            code=1510,
            message='Unknown device authorization',
        )


class DeviceAuthorizationExpired(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=410,
            code=1511,
            message='Device authorization has expired',
        )


class DeviceAuthorizationAlreadyApproved(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=409,
            code=1512,
            message='Device authorization has already been approved',
        )


class EpisodeUnknown(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1600,
            message='Unknown episode',
        )


class SearchException(APIException):
    def __init__(
        self, status_code: int = 400, extra: Any = None, message: str | None = None
    ) -> None:
        APIException.__init__(
            self,
            status_code=status_code,
            code=1700,
            message=message or 'Search error',
            extra=extra,
        )


class SortNotAllowed(APIException):
    def __init__(self, sort: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1800,
            message=f'Sort by: "{sort}" is not allowed',
            extra=[sort],
        )


class AppendFieldsNotAllowed(APIException):
    def __init__(self, fields: list[str]) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=1900,
            message='Append fields: "{}" are not allowed'.format(','.join(fields)),
            extra=fields,
        )


class ImageExternalDuplicate(APIException):
    def __init__(self, message: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2000,
            message=message,
        )


class ImageUnknown(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2001,
            message='Unknown image',
        )


class ImageNoData(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2003,
            message='No image data assigned. Please upload an image',
        )


class ImageWrongSize(APIException):
    def __init__(self, aspect_ratio: str) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2004,
            message=f'The image aspect ratio must be: {aspect_ratio}',
        )


class FileUploadNoFiles(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2100,
            message='Zero files was uploaded',
        )


class FileUploadUnrecognizedImage(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2101,
            message='Unrecognized image type. Please upload a JPG or PNG image',
        )


class PlayServerUnknown(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2200,
            message='Unknown play server',
        )


class PlayServerInviteInvalid(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2250,
            message='Invite id is invalid',
        )


class PlayServerInviteAlreadyHasAccess(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2251,
            message='The user does already have access to this play server',
        )


class PlayServerAccessUserNoAccess(APIException):
    def __init__(self) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2260,
            message="The user doesn't have access to this play server",
        )


class MovieUnknown(APIException):
    def __init__(self, movie_id: int) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2300,
            message=f'Unknown movie ({movie_id})',
        )


class MovieExternalDuplicated(APIException):
    def __init__(self, external_title: str, external_value: str, movie: Any) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=2305,
            message=(
                f'A movie with external name: "{external_title}" and id: '
                f'"{external_value}" does already exist'
            ),
            extra={
                'movie': movie,
                'external_title': external_title,
                'external_value': external_value,
            },
        )


class PersonExternalDuplicated(APIException):
    def __init__(self, external_title: str, external_value: str, person: Any) -> None:
        APIException.__init__(
            self,
            status_code=400,
            code=3005,
            message=(
                f'A person with external name: "{external_title}" and id: '
                f'"{external_value}" does already exist'
            ),
            extra={
                'person': person,
                'external_title': external_title,
                'external_value': external_value,
            },
        )
