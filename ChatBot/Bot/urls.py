from django.urls import path
from .views import webhook, chat, client_menu, \
complete_order, manage, home, menu, menu_add, category_add, edit_product, delete_product, category_manage, category_delete

urlpatterns = [
    path('', home, name='home'),
    path('webhook/', webhook, name='webhook'),
    path('chat/', chat, name='chat'),
    path('chat/<int:id>', chat, name='chat_id'),
    path('menu', menu, name='menu'),
    path('menu/add_product/', menu_add, name='menu_add'),
    path('menu/add_category/', category_add, name='category_add'),
    path('menu/edit/<int:id>', edit_product, name='edit_product'),
    path('menu/delete/<int:id>', delete_product, name='delete_product'),
    path('menu/<int:number>', client_menu, name='client_menu'),
    path('menu/<int:number>/<int:order>', complete_order, name='complete_order'),
    path('menu/manage_category', category_manage, name='category_manage'),
    path('menu/manage_category/delete/<int:id>', category_delete, name='category_delete'),
    path('manage/', manage, name='manage'),
    path('manage/<int:id>', manage, name='manage_id'),
]