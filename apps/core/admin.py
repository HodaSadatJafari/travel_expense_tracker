from django.contrib import admin
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from apps.core.models.users import CustomUser

class CustomUserAdmin(UserAdmin):

    list_display = [
        "id",
        "email",
        "is_superuser",
        "is_staff",
        "created_at",
    ]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (

                    "is_superuser",
                    "is_staff",
                    "password",
                    "groups",
                    "created_at",
                    "updated_at",
                    "id",
                ),
            },
        ),
    )
    list_editable = [
        "is_superuser",
        "is_staff",
        
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "id",
    ]

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    search_fields = [
        "id",
    ]


admin.site.register(CustomUser, CustomUserAdmin)
