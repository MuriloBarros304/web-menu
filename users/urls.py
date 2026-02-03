from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomLoginView, UserCreateView, UserViewSet, UserProfileView

# Router para o ViewSet (Gera /users/, /users/{id}/, /users/{id}/change_type/)
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='user-me'),
    
    path('', include(router.urls)),
]