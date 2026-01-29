"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_verified",
        "is_active",
        "date_joined",
    ]
    list_filter = ["user_type", "is_verified", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "cpf"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "cpf", "phone")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "LGPD",
            {"fields": ("lgpd_consent", "lgpd_consent_date")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "user_type",
                ),
            },
        ),
    )

    inlines = [ProfileInline, AddressInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "street",
        "city",
        "state",
        "zipcode",
        "is_default",
        "address_type",
    ]
    list_filter = ["state", "address_type", "is_default"]
    search_fields = ["user__email", "street", "city", "zipcode"]
