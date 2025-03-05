from rest_framework import routers
from .views import CustomAuthView, CheckAuthView, CustomTemplateView
from rest_framework.routers import DefaultRouter
from django.urls import include, path



urlpatterns = [
    path('', CustomTemplateView.as_view()),
    path('auth/', CustomAuthView.as_view(), name='custom_auth'),
    path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
]
