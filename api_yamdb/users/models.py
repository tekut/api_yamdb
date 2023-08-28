from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import UsernameValidator


class UserRoles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    """Custom User class"""
    username_validator = UsernameValidator()
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField('Email', max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        max_length=9,
        verbose_name='Роль',
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=100,
                                         null=True
                                         )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_user(self):
        return self.role == "user"
