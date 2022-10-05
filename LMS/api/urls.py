from django.urls import path, include
from rest_framework.authtoken.views import ObtainAuthToken

from .views import (Lms_api_root,)
# from .accounts.views import


app_name = "api"

urlpatterns = [
    path("", Lms_api_root, name="api_root"),
    path("auth_token/", ObtainAuthToken.as_view(), name="auth_token"),
    path("accounts/", include("accounts.urls")),
    path("management_system/", include("management_system.urls"))
]
