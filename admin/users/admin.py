from django.contrib import admin

from . import models


class User(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.User, User)
admin.site.register(models.Group)
