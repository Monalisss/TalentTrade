from django.urls import path
from . import consumers
#like url.py but for ws
websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/', consumers.ChatConsumer.as_asgi()),
]