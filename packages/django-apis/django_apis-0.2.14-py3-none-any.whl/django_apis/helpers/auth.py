import base64
from django_apis.exceptions import Forbidden
from jsonpath_ng.ext import parse as json_parser

__all__ = [
    "http_bearer_auth_protect",
    "http_basic_auth_protect",
    "apikey_auth_protect",
]


def http_bearer_auth_protect(request, apikeys, header="Authorization"):
    """Http Bearer请求头认证"""
    authorization = request.META.get("HTTP_" + header.upper(), None)
    if not authorization:
        raise Forbidden()
    if authorization.startswith("Bearer "):
        authorization = authorization[7:]
    if not authorization in apikeys:
        raise Forbidden()
    return authorization


def http_basic_auth_protect(request, username, password, header="Authorization"):
    """Http Basic请求头认证"""
    authorization = request.META.get("HTTP_" + header.upper(), None)
    if not authorization:
        raise Forbidden()
    if len(authorization) % 4:
        authorization += "=" * ((4 - len(authorization) % 4) % 4)
    authorization = base64.decodebytes(authorization.encode()).decode()
    if not ":" in authorization:
        raise Forbidden()
    username_input, password_input = authorization.split(":", 1)
    if username_input != username or password_input != password:
        raise Forbidden()
    return username, password


def apikey_auth_protect(
    request,
    apikeys,
    headers="apikey",
    query_fields=None,
    payload_fields=None,
    form_fields=None,
    cookie_fields=None,
):
    """开放式的apikey认证"""
    if isinstance(headers, str):
        headers = [headers]
    apikey_input = None
    if not apikey_input and headers:
        for header in headers:
            apikey_input = request.META.get("HTTP_" + header.upper(), None)
            if apikey_input:
                break
    if not apikey_input and cookie_fields:
        for field in cookie_fields:
            apikey_input = request.COOKIES.get(field, None)
            if apikey_input:
                break
    if not apikey_input and form_fields:
        for field in form_fields:
            apikey_input = request.POST.get(field, None)
            if apikey_input:
                break
    if not apikey_input and payload_fields:
        try:
            payload = json.loads(request.body)
        except:
            payload = {}
        for field in payload_fields:
            if field.startswith("$") or ("." in field):
                parser = json_parser(field)
                for item in parser.find(payload):
                    apikey_input = item.value
                    if apikey_input:
                        break
            else:
                apikey_input = payload.get(field, None)
                if apikey_input:
                    break
    if not apikey_input and query_fields:
        for field in query_fields:
            apikey_input = request.GET.get(field, None)
            if apikey_input:
                break
    if not apikey_input:
        raise Forbidden()
    if apikey_input.startswith("Bearer "):
        apikey_input = apikey_input[7:]
    elif apikey_input.startswith("Basic "):
        apikey_input = apikey_input[6:]
    if not apikey_input in apikeys:
        raise Forbidden()
    return apikey_input
