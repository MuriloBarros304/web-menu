from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    type = models.CharField(max_length=50, verbose_name='Tipo de Usuario', choices=[
        ('admin', 'Administrador'),
        ('customer', 'Cliente'),
        ('staff', 'Funcionário'),
    ])
    REQUIRED_FIELDS = ['email', 'type']
