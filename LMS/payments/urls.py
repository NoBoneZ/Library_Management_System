from django.urls import path

from .views import test

app_name = "payments"

urlpatterns = [
    path("", test, name="test")
]