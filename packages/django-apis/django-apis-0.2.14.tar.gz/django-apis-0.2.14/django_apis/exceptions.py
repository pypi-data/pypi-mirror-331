__all__ = [
    "BizError",
    "BadReqeust",
    "RequestValidationError",
    "AuthenticationFailed",
    "InsufficientBalance",
    "InvalidParameter",
    "Forbidden",
    "MethodNotAllowed",
    "UnsupportedMediaType",
    "InternalServerError",
    "ServerBusy",
]


class BizError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(code, message)

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]


# 400
class BadReqeust(BizError):
    """错误的请求。"""

    def __init__(self, code=400, message="Bad Reqeust"):
        super().__init__(code, message)


# 400
class RequestValidationError(BadReqeust):
    """请求参数验证错误。"""

    def __init__(self, code=400, message="Request Validation Error"):
        super().__init__(code, message)


# 401
class AuthenticationFailed(BizError):
    """认证失败。"""

    def __init__(self, code=401, message="Authentication Failed"):
        super().__init__(code, message)


# 402
class InsufficientBalance(BizError):
    """余额不足。"""

    def __init__(self, code=402, message="Insufficient Balance"):
        super().__init__(code, message)


# 403
class Forbidden(BizError):
    """权限不足。"""

    def __init__(self, code=403, message="Forbidden"):
        super().__init__(code, message)


# 405
class MethodNotAllowed(BizError):
    """不支持的HTTP请求方式。"""

    def __init__(self, code=405, message="Method Not Allowed"):
        super().__init__(code, message)


# 415
class UnsupportedMediaType(BizError):
    """不支持的媒体（Content-Type）类型。"""

    def __init__(self, code=415, message="Unsupported Media Type"):
        super().__init__(code, message)


# 422
class InvalidParameter(BizError):
    """参数错误。"""

    def __init__(self, code=422, message="Invalid Parameter"):
        super().__init__(code, message)


# 500
class InternalServerError(BizError):
    """服务器内部错误。"""

    def __init__(self, code=500, message="Internal Server Error"):
        super().__init__(code, message)


# 503
class ServerBusy(BizError):
    """服务器繁忙。"""

    def __init__(self, code=503, message="Server Busy"):
        super().__init__(code, message)
