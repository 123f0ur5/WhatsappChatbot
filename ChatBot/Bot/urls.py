from django.urls import path
from .views import webhook, chat, chatting, menu, complete_order

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
    path('chat/', chat, name='chat'),
    path('chat/<int:id>', chatting, name='chatting'),
    path('menu/<int:number>', menu, name='menu'),
    path('menu/<int:number>/<int:order>', complete_order, name='complete_order'),
]