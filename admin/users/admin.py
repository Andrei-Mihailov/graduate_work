from django.contrib import admin
import random
import string
from . import models

# генерация тестовых данных
# for i in range(5):
#     models.Group.objects.create(name="".join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

# domain = "example.com"
# for i in range(100):
#     username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
#     user = models.User.objects.create(email=f"{username}@{domain}")
#     for k in range(random.randint(1, 5)):
#         group = models.Group.objects.get(id=random.randint(1, 5))
#         user.group.add(group)


class Group(admin.ModelAdmin):
    list_display = ("name", "description")


class User(admin.ModelAdmin):
    fields = ("email", "group")
    readonly_fields = ("email",)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.User, User)
admin.site.register(models.Group, Group)
