from django.urls import path, include

from .views import (Lms_api_root,)
# from .accounts.views import


app_name = "api"

urlpatterns = [
    path("", Lms_api_root, name="api_root"),
    path("accounts/", include("accounts.urls")),
    path("management_system/", include("management_system.urls"))
]
