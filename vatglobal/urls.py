from django.urls import path, include
from django.views.generic import TemplateView

from .api_documentation_helpers.custom_renderer import custom_renderer_api

urlpatterns = [
    path(
        'api/',
        include('api.versions.urls')
    ),
    path(
        'openapi',
        custom_renderer_api,
        name='openapi_schema'
    ),
    path(
        'redoc/',
        TemplateView.as_view(
            template_name='redoc.html',
            extra_context={'schema_url': 'openapi-schema'}
        ),
        name='redoc'
    ),
]
