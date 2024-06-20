from django.urls import include, path
from . import views

urlpatterns = [
    path("register/",views.user_register , name='user_register'),
    path("login/",views.login, name='login')
]