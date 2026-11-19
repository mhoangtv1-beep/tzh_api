class TzhAPIException(Exception):
    pass

class TzhUserError(TzhAPIException):
    pass

class TzhLoginError(TzhAPIException):
    pass

class LoginMethodNotSupport(TzhAPIException):
    pass

class EncodePayloadError(TzhAPIException):
    pass

class DecodePayloadError(TzhAPIException):
    pass
