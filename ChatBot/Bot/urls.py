from django.urls import path
from .views import webhook, chat, chatting

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
    path('chat/', chat, name='chat'),
    path('chat/<int:id>', chatting, name='chatting')
]