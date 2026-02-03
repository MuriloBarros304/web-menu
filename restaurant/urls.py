from rest_framework.routers import DefaultRouter
from restaurant.views import DishViewSet, TableViewSet, OrderViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'dishes', DishViewSet, basename='dish')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls), name='restaurant'),
]