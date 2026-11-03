from django.contrib import admin
from .models import Item

admin.site.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "price")