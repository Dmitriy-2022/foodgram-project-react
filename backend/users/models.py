from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# def validate_username(value):
#     USERNAME_ME = 'Нельзя использовать "me" в качестве username'
#     USERNAME_EMPTY = 'Поле "username" не должно быть пустым'
#     if value == 'me' or '':
#         invalid_username = USERNAME_ME if (
#             value == 'me') else USERNAME_EMPTY
#         raise serializers.ValidationError(detail=[invalid_username])
#     result = re.findall(r'[^\w.@+-]', value)
#     if result:
#         raise serializers.ValidationError(
#             f'Некорректные символы в username:'
#             f' `{"`, `".join(set(result))}`.'
#         )
#     return value

class FoodgramUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.LENGTH_254,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=settings.LENGTH_150,
        unique=True,
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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
