from django.urls import path
from .consumers import *

print ('in ws path')
websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>",ChatroomConsumer.as_asgi()),
]
