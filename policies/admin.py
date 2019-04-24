from django.contrib import admin

from .models import (
    Policy,
)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ["name", "dependants_per_holder", "member_count", "dependant_count", ]
    search_fields = ["name", ]
