from register.views import register_request, cross_auth
from django.contrib.auth import views as auth_views
from django.urls import path


app_name = 'register'

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='register/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='register/logout.html'), name='logout'),
    path('signup/', register_request, name='signup'),
    path('cross-auth/', cross_auth, name='cross-auth')

]
