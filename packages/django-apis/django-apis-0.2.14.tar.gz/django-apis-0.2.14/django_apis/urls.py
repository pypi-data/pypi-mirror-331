from django.urls import path

from . import swagger_ui
from .settings import DJANGO_APIS_SWAGGER_UI_PATH


urlpatterns = [
    path(
        f"{DJANGO_APIS_SWAGGER_UI_PATH}",
        swagger_ui.swagger_ui_view,
        name="django_apis_swagger_ui_view",
    ),
    path(
        f"{DJANGO_APIS_SWAGGER_UI_PATH}init.js",
        swagger_ui.swagger_ui_init_js,
        name="django_apis_swagger_ui_init_js",
    ),
    path(
        f"{DJANGO_APIS_SWAGGER_UI_PATH}data.json",
        swagger_ui.swagger_ui_data,
        name="django_apis_swagger_ui_data",
    ),
]
