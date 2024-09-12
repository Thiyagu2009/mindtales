from django.contrib import admin

from restaurant.models import Menu, MenuItem
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

admin.site.register(MenuItem)
admin.site.register(Menu)
