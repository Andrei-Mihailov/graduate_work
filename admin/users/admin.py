from django.contrib import admin
import random
import string
from . import models


# for i in range(5):
#     models.Group.objects.create(name="".join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

# for i in range(100):
#     user = models.User.objects.create(username="".join(random.choices(string.ascii_letters, k=random.randint(10, 15))))
#     for k in range(random.randint(1, 5)):
#         group = models.Group.objects.get(id=random.randint(1, 5))
#         user.group.add(group)


class Group(admin.ModelAdmin):
    list_display = (
        'name',
        'description'
    )


class User(admin.ModelAdmin):
    fields = (
        'username',
        'group'
    )
    exclude = (
        'password',
        'last_login'
    )
    readonly_fields = (
        'username',
    )

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.User, User)
admin.site.register(models.Group, Group)
