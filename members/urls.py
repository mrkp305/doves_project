from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import (
    register_view, login_view, profile_view, add_dependant_view, view_dependant_view,
    dependants_view, edit_dependant_view, delete_dependant_view, claims_view, claim_cover_view,
    cash_request_view, cashbacks_view, delete_cash_back_view, index_view
)

app_name = "members"

dependant_patterns = [
    path('', dependants_view, name="dependants"),
    path("<int:pk>/", view_dependant_view, name="view_dependant"),
    path("<int:pk>/edit/", edit_dependant_view, name="edit_dependant"),
    path("<int:pk>/delete/", delete_dependant_view, name="delete_dependant"),
    path('add/', add_dependant_view, name="add_dependant"),
]

cash_patterns = [
    path('', cashbacks_view, name="cashbacks"),
    path('request/', cash_request_view, name="cashback_request"),
    path('<int:pk>/delete/', delete_cash_back_view, name="delete_cashback"),
]


claim_patterns = [
    path('', claims_view, name="claims"),
    path('<int:dependant>/add/', claim_cover_view, name="claim"),
]

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('profile/', profile_view, name='profile'),
    path('dependants/', include(dependant_patterns)),
    path('claims/', include(claim_patterns)),
    path('cashback/', include(cash_patterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
