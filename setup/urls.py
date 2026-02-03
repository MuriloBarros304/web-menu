from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls'), name='users'),
    path('api/', include('restaurant.urls'), name='restaurant'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]