from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import filters, permissions, status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from djoser import views

from recipes.models import Tag, Recipe, Ingredient
from .serializers import UsersSerializer, PasswordSerializer, TagSerializer, RecipeSerializer, IngredientSerializer

User = get_user_model()

@permission_classes([permissions.AllowAny])
class FoodgramUserViewSet(views.UserViewSet):
    http_method_names = ['post', 'get', 'delete']
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get_queryset(self):
        #  user = self.request.user
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
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@permission_classes([permissions.AllowAny])
class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
