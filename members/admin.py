from django.contrib import admin

from .models import (
    Member, Dependant
)

Member.get_marital_status_display.short_description = "Marital Status"
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "full_name", "age", "sex", "get_marital_status_display", "policy", "date_joined", "dependant_count",
    ]
    list_filter = ["sex", "policy", "date_joined", "marital_status", ]
    search_fields = ["first_name", "last_name", ]


Dependant.get_relationship_display.short_description = "Relationship"
@admin.register(Dependant)
class DependantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "age", "sex", "date_joined", "member_name", "get_relationship_display", ]
    list_filter = ["sex", "date_joined", "relationship", ]
    search_fields = ["first_name", "last_name", ]