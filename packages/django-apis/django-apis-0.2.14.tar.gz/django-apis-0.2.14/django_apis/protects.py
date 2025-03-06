import base64
from .exceptions import AuthenticationFailed
from .settings import DJANGO_APIS_APIKEY_HEADER_NAMES
from .settings import DJANGO_APIS_APIKEYS
from .settings import DJANGO_APIS_USERS

__all__ = [
    "apikey_protect",
    "http_basic_protect",
]


def http_basic_protect(request):
    """HTTP BASIC认证"""
    # 如果没有设置apiusers
    # 则无须进行http basic认证
    apiusers = DJANGO_APIS_USERS
    if not apiusers:
        return True
    userinfo = request.META.get("HTTP_AUTHORIZATION", None)
    if not userinfo:
        raise AuthenticationFailed(message="缺少HTTP BASIC认证参数，拒绝访问。")
    if userinfo.lower().startswith("basic "):
        userinfo = userinfo[6:].strip()
    try:
        username, password = (
            base64.decodebytes(userinfo.encode("utf-8")).decode("utf-8").split(":")
        )
    except Exception:
        raise AuthenticationFailed(message="无法解析的HTTP BASIC认证参数，拒绝访问。")
    passwords = apiusers.get(username, [])
    if not passwords:
        raise AuthenticationFailed(message="错误的认证信息，拒绝访问。")
    if isinstance(passwords, str):
        if password != passwords:
            raise AuthenticationFailed(message="错误的认证信息，拒绝访问。")
    else:
        if not password in passwords:
            raise AuthenticationFailed(message="错误的认证信息，拒绝访问。")
    return True


def apikey_protect(request):
    """APIKEY认证以及HTTP Bearer认证保护。"""
    # 如果没有设置apikeys
    # 则无须进行apikey认证
    apikeys = DJANGO_APIS_APIKEYS
    if apikeys and isinstance(apikeys, str):
        apikeys = DJANGO_APIS_APIKEYS and DJANGO_APIS_APIKEYS.split(",") or []
    if not apikeys:
        return True
    # 如果没有设置apikey header names
    # 则无须进行apikey认证
    header_names = DJANGO_APIS_APIKEY_HEADER_NAMES
    if header_names and isinstance(header_names, str):
        header_names = DJANGO_APIS_APIKEY_HEADER_NAMES.split(",")
    if not header_names:
        return True
    # 从请求头中获取apikey进行认证
    apikey = None
    for header_name in header_names:
        apikey = request.META.get(header_name, None)
        if apikey:
            break
    if not apikey:
        raise AuthenticationFailed(message="缺少APIKEY参数，拒绝访问。")
    if apikey.startswith("Bearer "):
        apikey = apikey[7:]
    if not apikey in apikeys:
        raise AuthenticationFailed(message="APIKEY检验失败！")
