from django.contrib import admin
from .models import Cookbook, CookbookMembership, CookbookInvitation

admin.site.register(Cookbook)
admin.site.register(CookbookMembership)
admin.site.register(CookbookInvitation)
