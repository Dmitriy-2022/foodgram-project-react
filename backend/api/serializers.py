from users.models import FoodgramUser
from recipes.models import Tag, Recipe, Ingredient
from rest_framework import serializers
from django.conf import settings


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodgramUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class PasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        max_length=settings.LENGTH_150,
    )

    class Meta:
        model = FoodgramUser
        fields = (
            'new_password',
            'id',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'image', 'ingredients',  'name', 'text', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )
