from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from users.models import FoodgramUser


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
        return f'{self.id}'


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.LENGTH_200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='ingredients',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления(мин.)',
        validators=[
            MinValueValidator(settings.MIN_TIME_COOK,
                              message=f'Время приготовления не может быть'
                                      f' меньше {settings.MIN_TIME_COOK}'
                              )
        ]
    )

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='amount',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_set',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'),
        ]

    def __str__(self):
        return f'{self.recipe.name}({self.recipe.id}) - {self.ingredient.id}'


class Follow(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        FoodgramUser,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        FoodgramUser,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Пользователь {self.user} добавил в в корзину {self.recipe}'

    class Meta:
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shop_cart'),
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        FoodgramUser,
        related_name='user',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Пользователь {self.user} добавил в избранное {self.recipe}'

    class Meta:
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'),
        ]
