import json
import inspect
import logging
import traceback
import functools

from zenutils import importutils
from zenutils import jsonutils
from zenutils import importutils
from pydantic import BaseModel
from pydantic import ValidationError

from django.http.response import HttpResponseBase
from django.http import JsonResponse

from .exceptions import BizError
from .exceptions import MethodNotAllowed
from .exceptions import UnsupportedMediaType
from .exceptions import RequestValidationError
from .exceptions import InternalServerError
from .constants import DJANGO_APIS_FUNC_PARAMETERS_KEY
from .constants import DJANGO_APIS_METHODS_KEY
from .constants import DJANGO_APIS_VIEW_FLAG_KEY
from .constants import DJANGO_APIS_VIEW_TAGS_KEY
from .constants import DJANGO_APIS_VIEW_SITE_KEY
from .constants import DJANGO_APIS_APIVIEW_INSTANCE_KEY
from .schemas import SimpleResponse
from .settings import DJANGO_API_VIEW

__all__ = [
    "Apiview",
    "apiview",
    "get_apiview",
]
_logger = logging.getLogger(__name__)


class Apiview(object):
    base_response_data_field = "data"
    base_response_class = SimpleResponse
    json_encoder = jsonutils.make_simple_json_encoder()

    def get_json_encoder(self):
        return self.json_encoder

    def __call__(self, methods="GET", tags=None, site="default"):
        methods = self.get_methods(methods)
        if tags and isinstance(tags, str):
            tags = [tags]

        def view(func):
            def inner_view(request, **path_kwargs):
                try:
                    self.request_method_check(request, methods)
                    func_data = self.get_func_data(
                        func,
                        request,
                        path_kwargs,
                    )
                    result = func(**func_data)
                    if isinstance(result, HttpResponseBase):
                        return result
                    else:
                        if isinstance(result, BaseModel):
                            result = result.model_dump()
                        return self.make_response(result)
                # 请求参数检验错误
                except ValidationError as error:
                    _logger.error(
                        "ValidationError: PATH=%s, GET=%s, POST=%s, FILES=%s, META=%s, error=%s",
                        request.path,
                        request.GET,
                        request.POST,
                        request.FILES,
                        request.META,
                        error,
                    )
                    error = RequestValidationError()
                    return self.make_error_response(
                        error.code,
                        error.message,
                        status_code=error.code,
                    )
                # json payload解析错误
                except UnsupportedMediaType as error:
                    _logger.error(
                        "UnsupportedMediaType: PATH=%s, GET=%s, POST=%s, FILES=%s, META=%s, error=%s",
                        request.path,
                        request.GET,
                        request.POST,
                        request.FILES,
                        request.META,
                        error,
                    )
                    return self.make_error_response(
                        error.code,
                        error.message,
                        status_code=415,
                    )
                # http请求方法检验错误
                except MethodNotAllowed as error:
                    _logger.error(
                        "MethodNotAllowed: PATH=%s, GET=%s, POST=%s, FILES=%s, META=%s, error=%s",
                        request.path,
                        request.GET,
                        request.POST,
                        request.FILES,
                        request.META,
                        error,
                    )
                    return self.make_error_response(
                        error.code,
                        error.message,
                        status_code=405,
                    )
                # 其它业务逻辑错误
                except BizError as error:
                    _logger.error(
                        "BizError: PATH=%s, GET=%s, POST=%s, FILES=%s, META=%s, error=%s",
                        request.path,
                        request.GET,
                        request.POST,
                        request.FILES,
                        request.META,
                        error,
                    )
                    return self.make_error_response(
                        error.code,
                        error.message,
                    )
                # 未处理的系统错误
                except Exception as error:
                    _logger.exception(
                        "InternalServerError: PATH=%s, GET=%s, POST=%s, FILES=%s, META=%s, error=%s",
                        request.path,
                        request.GET,
                        request.POST,
                        request.FILES,
                        request.META,
                        error,
                    )
                    error = InternalServerError()
                    return self.make_error_response(
                        error.code,
                        error.message,
                        status_code=error.code,
                    )

            setattr(func, DJANGO_APIS_VIEW_FLAG_KEY, True)
            setattr(func, DJANGO_APIS_VIEW_TAGS_KEY, tags)
            setattr(func, DJANGO_APIS_VIEW_SITE_KEY, site)
            setattr(func, DJANGO_APIS_METHODS_KEY, methods)
            setattr(func, DJANGO_APIS_APIVIEW_INSTANCE_KEY, self)
            setattr(func, "csrf_exempt", True)
            return functools.wraps(func)(inner_view)

        return view

    def get_methods(self, methods):
        if isinstance(methods, str):
            methods = [x.strip().upper() for x in methods.split(",")]
            methods = list(set(methods))
            methods.sort()
            return methods
        elif isinstance(methods, (list, str, tuple)):
            methods = list(set(methods))
            methods = [x.strip().upper() for x in methods]
            methods.sort()
            return methods
        else:
            _logger.warning(
                """django-apis' apiview get bad methods=%s, change it to the default value ["GET"].""",
                methods,
            )
            return ["GET"]

    def request_method_check(self, request, methods):
        if not request.method in methods:
            raise MethodNotAllowed()

    def make_response(self, data):
        return JsonResponse(
            {
                "code": 0,
                "message": "OK",
                "data": data,
            },
            encoder=self.get_json_encoder(),
            json_dumps_params={
                "ensure_ascii": False,
            },
        )

    def make_error_response(self, code, message, status_code=200):
        return JsonResponse(
            {
                "code": code,
                "message": message,
                "data": None,
            },
            encoder=self.get_json_encoder(),
            json_dumps_params={
                "ensure_ascii": False,
            },
            status=status_code,
        )

    def get_func_parameters(self, func):
        if hasattr(func, DJANGO_APIS_FUNC_PARAMETERS_KEY):
            return getattr(func, DJANGO_APIS_FUNC_PARAMETERS_KEY)
        func_parameters = inspect.signature(func).parameters
        setattr(func, DJANGO_APIS_FUNC_PARAMETERS_KEY, func_parameters)
        return func_parameters

    def get_func_data(self, func, request, path_kwargs):
        data = {}
        for name, param in self.get_func_parameters(func).items():
            if name == "request":
                data["request"] = request
            elif name == "payload":
                data["payload"] = self.get_func_payload_data(request, param.annotation)
            elif name == "form":
                data["form"] = self.get_func_form_data(request, param.annotation)
            elif name == "query":
                data["query"] = self.get_func_query_data(request, param.annotation)
            else:
                data[name] = path_kwargs.get(name, None)
        return data

    def get_func_query_data(self, request, type):
        query = self.get_clean_query_data(request)
        return self.request_validate(query, type)

    def get_func_form_data(self, request, type):
        form = self.get_clean_form_data(request)
        return self.request_validate(form, type)

    def get_func_payload_data(self, request, type):
        try:
            payload = json.loads(request.body)
        except Exception as error:
            raise UnsupportedMediaType()
        return self.request_validate(payload, type)

    def request_validate(self, data, type):
        if issubclass(type, BaseModel):
            return type.model_validate(data)
        elif callable(type):
            return type(data)
        else:
            return data

    def get_clean_query_data(self, request):
        data = {}
        for key in request.GET.keys():
            value = request.GET.getlist(key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            data[key] = value
        return data

    def get_clean_form_data(self, request):
        """可能为多媒体表单。"""
        data = {}
        for key in request.POST.keys():
            value = request.POST.getlist(key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            data[key] = value
        for key in request.FILES.keys():
            value = request.FILES.getlist(key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            data[key] = value
        return data


apiview = Apiview()


def get_apiview():
    result = DJANGO_API_VIEW
    if isinstance(result, str):
        result = importutils.import_from_string(result)
    if isinstance(result, Apiview):
        return result
    if callable(result):
        return result()
    raise BizError(code=500, message="Bad DJANGO_API_VIEW...")
