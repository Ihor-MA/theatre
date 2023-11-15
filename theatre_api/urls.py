from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/theatre/", include("theatre.urls", namespace="cinema")),
    path("api/user/", include("user.urls", namespace="user")),
    path("__debug__/", include("debug_toolbar.urls")),
]
