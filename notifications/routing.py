from django.urls import re_path

from .consumers import WorkspaceConsumer


websocket_urlpatterns = [
    re_path(r'^ws/organization/(?P<organization_id>[0-9a-f\-]+)/$', WorkspaceConsumer.as_asgi()),
]
