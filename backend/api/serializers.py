import base64
import six
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers, permissions
from rest_framework.decorators import action

from users.models import FoodgramUser
from recipes.models import (
    ShoppingCart, Tag, Recipe,
    Ingredient, RecipeIngredient, Follow, Favorite
    )

User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, author=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            is_subscribed = Follow.objects.filter(
                user=request.user, author=instance).exists()
        else:
            is_subscribed = False
        representation['is_subscribed'] = is_subscribed
        return representation


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension
        return extension


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', )
        read_only_fields = ('name', 'measurement_unit', )


class AmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source='recipe_set', many=True)
    tags = TagRecipeSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags',  'author',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None)
    ingredients = AmountIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags', 'image', 'name',
            'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []

        if len(ingredients) < 1:
            raise serializers.ValidationError(
                'Должен быть хотя бы 1 ингредиент!')
        if len(data['tags']) < 1:
            raise serializers.ValidationError(
                'Должен быть хотя бы 1 тег!')
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.!')

        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше ноля!')

            ingredients_list.append(ingredient['id'])

        return data

    def load_data(self, ingredients, instance):
        list_obj = []

        for ingredient in ingredients:
            obj = RecipeIngredient(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=instance,
            )
            list_obj.append(obj)

        RecipeIngredient.objects.bulk_create(list_obj)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance).data

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)

        recipe.tags.set(tags)
        self.load_data(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')

        if ingredients is not None:
            instance.ingredients.clear()

        self.load_data(ingredients, instance)

        return super().update(instance, validated_data)


class SmallReadRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = SmallReadRecipeSerializer(source='author', many=True)

    class Meta:
        model = FoodgramUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, author=obj).exists()
        return False
