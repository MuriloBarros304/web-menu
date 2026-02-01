from django.urls import path
from .views import CustomLoginView, UserCreateView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
]