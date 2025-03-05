from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):

    model = User
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    search_fields = [
        'email',
        'username',
        'first_name',
        'last_name'
    ]
    list_filter = [
        'is_superuser',
        'is_staff',
        'is_active'
    ]


admin.site.register(User, UserAdmin)
