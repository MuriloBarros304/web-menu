from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    type = models.CharField(max_length=50, verbose_name='Tipo de Usuário', choices=[
        ('admin', 'Administrador'),
        ('customer', 'Cliente'),
        ('staff', 'Funcionário'),
    ],
    default='customer')
    REQUIRED_FIELDS = ['email', 'type']

