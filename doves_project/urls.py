
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from members.views import index_view, instant_cover_view, isucc_view, view_request_view, logout_view, payment_view, transaction_check_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("members/", include('members.urls')),
    path("", index_view, name="index"),
    path("get-instant-cover/", instant_cover_view, name="instant"),
    path("success-instant-cover/", isucc_view, name="succ"),
    path("view-request/<int:pk>/", view_request_view, name="view_request"),
    path("pay-for-request/<int:pk>/", payment_view, name="pay_request"),
    path("check_paynow_transaction_status/<int:pk>/",
         transaction_check_view, name="check_paynow_transaction_status"),

    path("logout/", logout_view, name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
