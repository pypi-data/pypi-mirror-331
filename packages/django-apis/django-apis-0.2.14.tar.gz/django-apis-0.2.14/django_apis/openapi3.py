import re
import json
import inspect
import typing

from zenutils import treeutils

from openapi_pydantic import OpenAPI
from openapi_pydantic.util import PydanticSchema
from openapi_pydantic.util import construct_open_api_with_schema_class

from django.apps import apps
from django.urls import get_resolver
from django.utils.translation import gettext
from django.conf import settings

from .constants import DJANGO_APIS_METHODS_KEY
from .constants import DJANGO_APIS_VIEW_FLAG_KEY
from .constants import DJANGO_APIS_VIEW_TAGS_KEY
from .constants import DJANGO_APIS_VIEW_SITE_KEY
from .constants import DJANGO_APIS_APIVIEW_INSTANCE_KEY
from .constants import DJANGO_APIS_OPENAPI_VERSION_DEFAULT
from .constants import DJANGO_APIS_OPENAPI_DESCRIPTION_DEFAULT
from .settings import DJANGO_APIS_OPENAPI_TAGS
from .settings import DJANGO_APIS_OPENAPI_SERVERS
from .settings import DJANGO_APIS_OPENAPI_TITLES
from .settings import DJANGO_APIS_OPENAPI_VERSIONS
from .settings import DJANGO_APIS_OPENAPI_DESCRIPTIONS
from .settings import DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS
from .schemas import ResponseBase


def get_default_title(site="default"):
    """获取默认的工程名称。"""
    return settings.ROOT_URLCONF.split(".")[0]


def get_tags_from_paths(paths):
    """获取所有提供了接口的应用标签列表。"""
    all_tags = []
    for path, path_info in paths.items():
        for method, method_info in path_info.items():
            tags = set(method_info.get("tags", []))
            all_tags += tags
    return set(all_tags)


def get_setting_tags(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_TAGS`设置。

    完整的`DJANGO_APIS_OPENAPI_TAGS`案例：

    ```python
    DJANGO_APIS_OPENAPI_TAGS = {
        "default": [
            {"name": "test1", "description": "测试1"},
        ],
        "another": [
            {"name": "test2", "description": "测试2"},
        ]
    }
    ```
    """
    if isinstance(DJANGO_APIS_OPENAPI_TAGS, dict):
        return DJANGO_APIS_OPENAPI_TAGS.get(
            site, DJANGO_APIS_OPENAPI_TAGS.get("default", [])
        )
    else:
        return DJANGO_APIS_OPENAPI_TAGS


def get_site_servers(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_SERVERS`设置。

    完整的`DJANGO_APIS_OPENAPI_SERVERS`案例：

    ```python
    DJANGO_APIS_OPENAPI_SERVERS = {
        "default": [
            {"url": "http://127.0.0.1:8000", "description": "本地开发环境"},
            {"url": "http://192.168.1.1", "description": "测试环境"},
        ],
        "another": [
            {"url": "http://192.168.1.1:8000", "description": "本地开发环境"},
            {"url": "http://192.168.1.1:8001", "description": "测试环境"},
        ]
    }
    ```

    """
    if isinstance(DJANGO_APIS_OPENAPI_SERVERS, dict):
        return DJANGO_APIS_OPENAPI_SERVERS.get(
            site, DJANGO_APIS_OPENAPI_SERVERS.get("default", [])
        )
    else:
        return DJANGO_APIS_OPENAPI_SERVERS


def get_site_title(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_TITLES`设置。

    完整的`DJANGO_APIS_OPENAPI_TITLES`案例：

    ```python
    DJANGO_APIS_OPENAPI_TITLES = {
        "default": "标题1",
        "another": "标题2"
    }
    ```

    """
    if isinstance(DJANGO_APIS_OPENAPI_TITLES, dict):
        return DJANGO_APIS_OPENAPI_TITLES.get(
            site,
            DJANGO_APIS_OPENAPI_TITLES.get("default", get_default_title(site=site)),
        )
    else:
        return DJANGO_APIS_OPENAPI_TITLES


def get_site_version(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_VERSIONS`设置。

    完整的`DJANGO_APIS_OPENAPI_VERSIONS`案例：

    ```python
    DJANGO_APIS_OPENAPI_VERSIONS = {
        "default": "标题1",
        "another": "标题2"
    }
    ```
    """
    if isinstance(DJANGO_APIS_OPENAPI_VERSIONS, dict):
        return DJANGO_APIS_OPENAPI_VERSIONS.get(
            site,
            DJANGO_APIS_OPENAPI_VERSIONS.get(
                "default",
                DJANGO_APIS_OPENAPI_VERSION_DEFAULT,
            ),
        )
    else:
        return DJANGO_APIS_OPENAPI_VERSIONS


def get_site_description(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_DESCRIPTIONS`设置。

    完整的`DJANGO_APIS_OPENAPI_DESCRIPTIONS`案例：

    ```python
    DJANGO_APIS_OPENAPI_DESCRIPTIONS = {
        "default": "描述1",
        "another": "描述2"
    }
    ```

    """
    if isinstance(DJANGO_APIS_OPENAPI_DESCRIPTIONS, dict):
        return DJANGO_APIS_OPENAPI_DESCRIPTIONS.get(
            site,
            DJANGO_APIS_OPENAPI_DESCRIPTIONS.get(
                "default",
                DJANGO_APIS_OPENAPI_DESCRIPTION_DEFAULT,
            ),
        )
    else:
        return DJANGO_APIS_OPENAPI_DESCRIPTIONS


def get_site_security_schemes(site="default"):
    """从settings.py中获取`DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS`设置。

    完整的`DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS`案例：

    ```python
    DJANGO_APIS_OPENAPI_DESCRIPTIONS = {
        "default": {
            "BasicAuth": {
                "type": "http",
                "scheme": "basic",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            },
            "ApikeyAuth": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
            },
            "OpenID": {
                "type": "openIdConnect",
                "openIdConnectUrl": "https://example.com/.well-known/openid-configuration",
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://example.com/oauth/authorize",
                        "tokenUrl": "https://example.com/oauth/token",
                        "scopes": {
                            "read": "Grants read access",
                            "write": "Grants write access",
                            "admin": "Grants access to admin operations",
                        },
                    }
                },
            },
        },
        "another": {
            "BasicAuth": {
                "type": "http",
                "scheme": "basic",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            },
            "ApikeyAuth": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
            },
            "OpenID": {
                "type": "openIdConnect",
                "openIdConnectUrl": "https://example.com/.well-known/openid-configuration",
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://example.com/oauth/authorize",
                        "tokenUrl": "https://example.com/oauth/token",
                        "scopes": {
                            "read": "Grants read access",
                            "write": "Grants write access",
                            "admin": "Grants access to admin operations",
                        },
                    }
                },
            },
        },
    }
    ```

    """

    if "default" in DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS:
        return DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS.get(
            site,
            DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS.get(
                "default",
                {},
            ),
        )
    else:
        return DJANGO_APIS_OPENAPI_SECURITY_DEFINITIONS


def get_tags(paths, site="default"):
    """获取全局应用标签信息列表。"""
    all_tags = []
    # 从paths中提取的所有tag名称
    all_tag_names = get_tags_from_paths(paths)
    # 加载用户配置的tags
    # 如果没有接口使用到该tag则忽略
    for tag in get_setting_tags(site=site):
        tag_name = tag.get("name", "")
        if not tag_name in all_tag_names:
            continue
        all_tags.append(tag)
    # 加载app_lable作为tags
    # 但如果与用户配置的tags重名则忽略
    for app in apps.get_app_configs():
        tag_name = app.label
        if not tag_name in all_tag_names:
            continue
        all_tags.append(
            {
                "name": tag_name,
                "description": gettext(app.verbose_name),
            }
        )
    return all_tags


def get_query_parameters(query_schema):
    """获取url参数定义。"""
    parameters = []
    required = query_schema.get("required", [])
    for prop_name, prop_info in query_schema["properties"].items():
        prop_schema = {}
        if "type" in prop_info:
            prop_schema["type"] = prop_info["type"]
        if "anyOf" in prop_info:
            prop_schema["anyOf"] = prop_info["anyOf"]
        if "default" in prop_info:
            prop_schema["default"] = prop_info["default"]
        parameters.append(
            {
                "in": "query",
                "name": prop_name,
                "description": prop_info.get("description", prop_info.get("title", "")),
                "schema": prop_schema,
                "required": prop_name in required,
            }
        )
    return parameters


def has_file_field(parameter_info):
    """判断当前接口是否需要上传文件。"""
    if parameter_info.annotation == inspect._empty:
        return False
    return '"binary"' in parameter_info.annotation.schema_json()


def get_simple_type(type):
    """处理简单参数类型的定义。"""
    if issubclass(type, str):
        return {"type": "string"}
    elif issubclass(type, int):
        return {"type": "integer"}
    elif issubclass(type, float):
        return {"type": "number"}
    else:
        return {}


def get_path_parameters(parameter_name, parameter_info):
    """获取路径参数定义。"""
    return [
        {
            "in": "path",
            "name": parameter_name,
            "schema": get_simple_type(parameter_info.annotation),
            "required": True,
        }
    ]


def get_view_methods(view):
    """从视图函数中获取视图支持的HTTP请求方法列表。"""
    return getattr(
        view,
        DJANGO_APIS_METHODS_KEY,
        ["GET"],
    )


def format_tags(tags):
    """格式化标签。总是为字符串数组。"""
    if isinstance(tags, str):
        return [tags]
    elif isinstance(tags, (list, set, tuple)):
        tags = list(tags)
        tags.sort()
        return tags
    else:
        return []


def is_django_apis_view(view, site="default"):
    """判断视图函数是否为使用`django-apis`提供的`apiview`方法注解的函数。"""
    is_django_apis_view_flag = getattr(view, DJANGO_APIS_VIEW_FLAG_KEY, False)
    is_site_flag = getattr(view, DJANGO_APIS_VIEW_SITE_KEY, "default") == site
    return is_django_apis_view_flag and is_site_flag


def get_tags_mapping():
    """创建应用标签查询表。"""
    modules_mapping = treeutils.SimpleRouterTree()
    for app in apps.get_app_configs():
        modules_mapping.index(app.module.__spec__.name, app.label)
    return modules_mapping


def make_generic_response_type(type_class, view, apiview_instance):
    """构建接口响应数据模型。"""
    name = (
        ".".join([view.__module__, view.__name__]).replace(".", "_").title()
        + "_Response"
    )
    new_type = type(
        name,
        (apiview_instance.base_response_class,),
        {
            apiview_instance.base_response_data_field: None,
            "__annotations__": {
                apiview_instance.base_response_data_field: type_class,
            },
        },
    )
    return new_type


def get_response_schema(type_class, view, apiview_instance):
    """获得接口响应数据模型。"""
    if type_class == inspect._empty:
        return {}
    elif type(type_class) == typing._GenericAlias:
        return PydanticSchema(
            schema_class=make_generic_response_type(
                type_class,
                view,
                apiview_instance,
            )
        )
    elif issubclass(type_class, ResponseBase):
        return PydanticSchema(
            schema_class=type_class,
        )
    else:
        return PydanticSchema(
            schema_class=make_generic_response_type(
                type_class,
                view,
                apiview_instance,
            )
        )


def get_securities(site="default"):
    """为接口添加认证方式。"""
    securities = [{}]
    for key in get_site_security_schemes(site=site).keys():
        securities.append({key: []})
    return securities


def get_view_schema(view, tags=None, site="default"):
    """获取视图定义。"""
    schema = {}
    description = view.__doc__ or ""
    apiview_instance = getattr(view, DJANGO_APIS_APIVIEW_INSTANCE_KEY, None)
    apiview_tags = getattr(view, DJANGO_APIS_VIEW_TAGS_KEY, None)
    if not apiview_tags:
        apiview_tags = format_tags(tags)
    info = {
        "summary": description and description.splitlines()[0] or "",
        "description": description,
        "tags": apiview_tags,
        "security": get_securities(site=site),
    }
    signature = inspect.signature(view)
    for parameter_name, parameter_info in signature.parameters.items():
        # 处理request参数。特殊参数，不需要体现在swagger中。
        if parameter_name == "request":
            # 忽略request参数
            # 无须处理
            pass
        # 处理json payload请求体
        elif parameter_name == "payload":
            info["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": (parameter_info.annotation != inspect._empty)
                        and PydanticSchema(schema_class=parameter_info.annotation)
                        or {},
                    },
                },
            }
        # 处理表单请求体
        elif parameter_name == "form":
            mimetype = "application/x-www-form-urlencoded"
            if has_file_field(parameter_info):
                mimetype = "multipart/form-data"
            info["requestBody"] = {
                "required": True,
                "content": {
                    mimetype: {
                        "schema": (parameter_info.annotation != inspect._empty)
                        and PydanticSchema(schema_class=parameter_info.annotation)
                        or {},
                    },
                },
            }
        # 处理url参数
        elif parameter_name == "query":
            if not "parameters" in info:
                info["parameters"] = []
            info["parameters"] += (
                (parameter_info.annotation != inspect._empty)
                and get_query_parameters(parameter_info.annotation.schema())
                or []
            )

        # @todo: 添加headers, cookies参数支持
        # 处理path参数
        else:
            if not "parameters" in info:
                info["parameters"] = []
            info["parameters"] += get_path_parameters(parameter_name, parameter_info)
    # 处理响应体
    info["responses"] = {
        "200": {
            "description": "Success",
            "content": {
                "application/json": {
                    "schema": get_response_schema(
                        signature.return_annotation,
                        view,
                        apiview_instance,
                    ),
                }
            },
        }
    }
    # 为每种支持的请求方法生成接口定义
    methods = get_view_methods(view)
    for method in methods:
        schema[method.lower()] = info
    return schema


def get_paths(site="default"):
    """获取所有接口定义。"""
    paths = {}
    tags_mapping = get_tags_mapping()
    global_urls = get_resolver().reverse_dict
    for view_item in global_urls.lists():
        # 获取当前视图的的处理函数
        view_func = view_item[0]
        if isinstance(view_func, str):
            try:
                view_func = resolve(reverse(view_func)).func
            except Exception:
                continue
        # 如果不是django-apis视图，则忽略
        if not is_django_apis_view(view_func, site=site):
            continue
        # 查找到当前视图函数所在应用标签，作为本接口的tag_name
        tag_name, _ = tags_mapping.get_best_match(view_func.__module__)
        if not tag_name:
            tag_name = "__all__"
        # 遍历所有视图公开的paths
        view_paths = view_item[1]
        for view_path in view_paths:
            path = "/" + view_path[0][0][0]
            path = re.sub("\\%\\(([^\\)]*)\\)s", "{\\1}", path)
            paths[path] = get_view_schema(view_func, tag_name, site=site)
    return paths


def get_docs(site="default"):
    """获取swagger数据。"""
    paths = get_paths(site=site)
    tags = get_tags(paths, site=site)
    openapi = construct_open_api_with_schema_class(
        OpenAPI.model_validate(
            {
                "openapi": "3.1.0",
                "servers": get_site_servers(site=site),
                "info": {
                    "title": get_site_title(site=site),
                    "version": get_site_version(site=site),
                    "description": get_site_description(site=site),
                },
                "tags": tags,
                "paths": paths,
                "components": {
                    "securitySchemes": get_site_security_schemes(site=site),
                },
            }
        )
    )
    return json.loads(
        openapi.json(
            by_alias=True,
            exclude_none=True,
        )
    )
