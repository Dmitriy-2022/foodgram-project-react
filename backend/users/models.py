from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class FoodgramUser(AbstractUser):
    REQUIRED_FIELDS = ['username', 'id', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.LENGTH_254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.LENGTH_150,
        unique=True,
        blank=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.LENGTH_150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LENGTH_150,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.LENGTH_150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
