from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import (
    register_view, login_view, profile_view
)

app_name = "members"
urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('profile/', profile_view, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
