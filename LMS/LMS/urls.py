"""LMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('LMS-restricted-path/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("management_system/", include("management_system.urls")),
    path("", RedirectView.as_view(url="management_system/")),
    path("payments/", include("payments.urls")),
    path("api/", include("api.urls")),
    path("api/accounts/", include("api.accounts.urls")),
    path("api/management_system_api/", include("api.management_system.urls")),
    path("api_auth/", include("rest_framework.urls"))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
