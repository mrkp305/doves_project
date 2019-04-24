from django.contrib import admin

from .models import (
    Member, Dependant
)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "full_name", "age", "sex", "marital_status_display", "policy", "date_joined", "dependant_count",
    ]
    list_filter = ["sex", "policy", "date_joined", "marital_status", ]
    search_fields = ["first_name", "last_name", ]


@admin.register(Dependant)
class DependantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "age", "sex", "date_joined", "member_name", "relationship_display", ]
    list_filter = ["sex", "date_joined", "relationship", ]
    search_fields = ["first_name", "last_name", ]