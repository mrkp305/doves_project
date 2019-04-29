from django.contrib import admin

from .models import (
    Member, Dependant, Claim, Request, Cashback
)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "full_name", "age", "sex", "marital_status_display", "policy", "cash_back_eligible", "date_joined", "dependant_count",
    ]
    list_filter = ["sex", "policy", "date_joined", "marital_status", ]
    search_fields = ["first_name", "last_name", ]


@admin.register(Dependant)
class DependantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "age", "sex", "date_joined", "member_name", "relationship_display", "is_deceased", ]
    list_filter = ["sex", "date_joined", "relationship", "is_deceased", ]
    search_fields = ["first_name", "last_name", ]


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ["dependant", "date_of_claim", "place_of_death", "date_of_death", ]
    list_filter = ["date_of_claim", ]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "national_id", "email_address", "phone", "address", "requested", ]
    list_filter = ["created", ]

@admin.register(Cashback)
class CashbackAdmin(admin.ModelAdmin):
    list_display = ["member", "amount", "paid_out", ]
    list_filter = ["created", "paid_out", ]
    search_fields = ["member", ]
