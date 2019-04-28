from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import (
    register_view, login_view, profile_view, add_dependant_view, view_dependant_view,
    dependants_view, edit_dependant_view, delete_dependant_view
)

app_name = "members"

dependant_patterns = [
    path('', dependants_view, name="dependants"),
    path("<int:pk>/", view_dependant_view, name="view_dependant"),
    path("<int:pk>/edit/", edit_dependant_view, name="edit_dependant"),
    path("<int:pk>/delete/", delete_dependant_view, name="delete_dependant"),
    path('add/', add_dependant_view, name="add_dependant"),
]

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('profile/', profile_view, name='profile'),
    path('dependants/', include(dependant_patterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
