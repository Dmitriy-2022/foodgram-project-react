from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import filters, permissions, status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from djoser import views
from django.shortcuts import get_object_or_404

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient
from .serializers import ReadRecipeSerializer, UsersSerializer, PasswordSerializer, TagSerializer, CreateUpdateRecipeSerializer, IngredientSerializer

User = get_user_model()
SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

@permission_classes([permissions.AllowAny])
class FoodgramUserViewSet(views.UserViewSet):
    http_method_names = ['post', 'get', 'delete']
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    @action(detail=False,
            methods=['get'],
            url_path='me',
            )
    def me(self, request):
        user = request.user
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    @action(["post"], detail=False)
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


@permission_classes([permissions.AllowAny])
class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@permission_classes([permissions.AllowAny])
class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return CreateUpdateRecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

@permission_classes([permissions.AllowAny])
class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
