from django.contrib import admin
from .models import Messages, Contacts, Products, Categories, Orders, Order_Products

# Register your models here.

admin.site.register(Messages)
admin.site.register(Contacts)
admin.site.register(Products)
admin.site.register(Categories)
admin.site.register(Orders)
admin.site.register(Order_Products)