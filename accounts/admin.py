from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'is_superuser')

    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {
            'fields': ('role', 'email_otp', 'otp_created_at'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'fields': ('role'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
