from users.models import FoodgramUser
from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient
from rest_framework import serializers
from django import core
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import filters, permissions, status
from django.core.files.base import ContentFile
import base64
import six
import uuid

User = get_user_model()


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
        extension = "jpg" if extension == "jpeg" else extension
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
    # amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', )


class AmountSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.StringRelatedField(read_only=True)
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class TagRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    # ingredients = serializers.SerializerMethodField()
    tags = TagRecipeSerializer(read_only=True, many=True)
   

    # def get_ingredients(self, obj):
    #     print(obj)
    #     ings = RecipeIngredient.objects.filter(recipe=obj).all()
    #     print(ings)
    #     return RecipeIngredientSerializer(ings, many=True).data

    class Meta:
        model = Recipe
        fields = ('id', 'tags',  'author',
                  'ingredients',  'name', 'image',
                  'text', 'cooking_time'
                  )


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None)
    ingredients = AmountIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags', 'image', 'name',
            'text', 'cooking_time'
        )

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance).data

    def create(self, validated_data):
        list_obj = []
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            obj = RecipeIngredient(
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'],
                recipe=recipe,
            )
            list_obj.append(obj)

        RecipeIngredient.objects.bulk_create(list_obj)
        return recipe
    
    def update(self, instance, validated_data):
        # instance.ingredients = validated_data.get('ingredients', instance.ingredients)
        # instance.tags = validated_data.get('tags', instance.tags)
        ingredients_data = validated_data.pop('ingredients')
        ingredients = instance.ingredients
        # tags = validated_data.pop('tags')

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()

        # print(instance.ingredients)
        # for ingredient_data in ingredients_data:
        #     print('Зашел', ingredient_data)
        #     print(ingredients.ingredient_id)
        #     ingredients.id = ingredient_data.get('id', ingredients.id)
        #     ingredients.amount = ingredient_data.get('amount', ingredients.amount)

        # instance.save()
        return instance
