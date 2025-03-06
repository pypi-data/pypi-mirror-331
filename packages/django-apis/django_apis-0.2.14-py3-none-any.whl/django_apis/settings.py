import yaml

import django_environment_settings
from django.urls import reverse_lazy


__all__ = [
    "DJANGO_APIS_APIKEY_HEADER_NAMES",
    "DJANGO_APIS_APIKEYS",
]

# -----------------------------------------------------------------------------
# DJANGO APIS相关配置
# -----------------------------------------------------------------------------
# DJANGO_API_VIEW
DJANGO_API_VIEW = django_environment_settings.get(
    "DJANGO_API_VIEW",
    "django_apis.views.apiview",
)
# DJANGO_APIS_SWAGGER_UI_PATH
DJANGO_APIS_SWAGGER_UI_PATH = django_environment_settings.get(
    "DJANGO_APIS_SWAGGER_UI_PATH",
    "docs/",
)
if DJANGO_APIS_SWAGGER_UI_PATH.startswith("/"):
    DJANGO_APIS_SWAGGER_UI_PATH = DJANGO_APIS_SWAGGER_UI_PATH[1:]
if not DJANGO_APIS_SWAGGER_UI_PATH.endswith("/"):
    DJANGO_APIS_SWAGGER_UI_PATH += "/"
# DJANGO_APIS_OPENAPI_TAGS
DJANGO_APIS_OPENAPI_TAGS = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_TAGS",
    [],
)
# DJANGO_APIS_OPENAPI_SERVERS
DJANGO_APIS_OPENAPI_SERVERS = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_SERVERS",
    {
        "default": [
            {"url": "http://127.0.0.1:8000", "description": "Local Development"},
        ]
    },
)
# DJANGO_APIS_OPENAPI_TITLES
DJANGO_APIS_OPENAPI_TITLES = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_TITLES",
    {},
    aliases=[
        "DJANGO_APIS_OPENAPI_TITLE",
    ],
)
# DJANGO_APIS_OPENAPI_VERSIONS
DJANGO_APIS_OPENAPI_VERSIONS = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_VERSIONS",
    {},
    aliases=[
        "DJANGO_APIS_OPENAPI_VERSION",
    ],
)
# DJANGO_APIS_OPENAPI_DESCRIPTIONS
DJANGO_APIS_OPENAPI_DESCRIPTIONS = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_DESCRIPTIONS",
    {},
    aliases=[
        "DJANGO_APIS_OPENAPI_DESCRIPTION",
    ],
)
# DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS
DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS",
    {},
    aliases=[
        "DJANGO_APIS_OPENAPI_SECURITY_DEFINITION",
    ],
)
# DJANGO_APIS_SWAGGER_LOGIN_REQUIRED
DJANGO_APIS_SWAGGER_LOGIN_REQUIRED = django_environment_settings.get(
    "DJANGO_APIS_SWAGGER_LOGIN_REQUIRED",
    True,
)
# DJANGO_APIS_OPENAPI_LOGIN_URL
DJANGO_APIS_OPENAPI_LOGIN_URL = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_LOGIN_URL",
    reverse_lazy("admin:login"),
)
# DJANGO_APIS_OPENAPI_SITES
DJANGO_APIS_OPENAPI_SITES = django_environment_settings.get(
    "DJANGO_APIS_OPENAPI_SITES",
    ["default"],
)
# -----------------------------------------------------------------------------
# HTTP APIKEY认证相关配置
# -----------------------------------------------------------------------------
# APIKEY认证允许的请求头
DJANGO_APIS_APIKEY_HEADER_NAMES = django_environment_settings.get(
    "DJANGO_APIS_APIKEY_HEADER_NAMES",
    "HTTP_AUTHORIZATION,HTTP_X_APIKEY,HTTP_APIKEY",
)
# APIKEY认证允许的授权码
DJANGO_APIS_APIKEYS = django_environment_settings.get(
    "DJANGO_APIS_APIKEYS",
    None,
    aliases=[
        "DJANGO_APIS_APIKEY",
    ],
)

DJANGO_APIS_USERS = django_environment_settings.get(
    "DJANGO_APIS_USERS",
    "{}",
)
if isinstance(DJANGO_APIS_USERS, str):
    DJANGO_APIS_USERS = yaml.safe_load(DJANGO_APIS_USERS)
