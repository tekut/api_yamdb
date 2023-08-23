from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRoles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    """Custom User class"""

    role = models.CharField(
        max_length=9,
        verbose_name='Роль',
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
