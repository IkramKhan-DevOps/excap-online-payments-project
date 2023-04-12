from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from webapps2023.settings import ENVIRONMENT


def home_view(request):
    return redirect("register:login")


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', home_view, name='home'),
    path('', include('register.urls', namespace='register')),
    path('', include('payapp.urls', namespace='payapp')),
]

if ENVIRONMENT != 'server':
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls"))
    ]
