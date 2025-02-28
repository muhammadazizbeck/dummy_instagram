from .views import CreateUserApiView
from django.urls import path

urlpatterns = [
    path('signup/',CreateUserApiView.as_view(),name='signup')
]