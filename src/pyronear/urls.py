from django.contrib import admin
from django.urls import path, include

from pyronear.apps.user.resources import UserResource

API_BASE = "pyronear/"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_BASE, include(UserResource().urls))
]
