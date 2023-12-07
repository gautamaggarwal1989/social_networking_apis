from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from .views import SignUpView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup')
]
