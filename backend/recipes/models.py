from django.db import models
from users.models import FoodgramUser
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LENGTH_200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в НЕХ',
        max_length=settings.LENGTH_7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=settings.LENGTH_200,
        unique=True,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LENGTH_200,
    )
    measurement_unit = models.CharField(
        verbose_name='Ед. изм.',
        max_length=settings.LENGTH_200,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.LENGTH_200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    time = models.IntegerField(
        verbose_name='Время приготовления(мин.)'
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    count = models.PositiveIntegerField(
        verbose_name='Количество',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'
