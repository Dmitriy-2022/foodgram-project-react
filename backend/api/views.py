from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from djoser import views
from django.shortcuts import get_object_or_404

from recipes.models import (
    Tag, Recipe, Ingredient,
    Follow, Favorite, ShoppingCart
    )
from .serializers import (
    SmallReadRecipeSerializer, ReadRecipeSerializer,
    UsersSerializer, PasswordSerializer, TagSerializer,
    CreateUpdateRecipeSerializer, IngredientSerializer, FollowSerializer
    )


User = get_user_model()
SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class MyPaginator(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 1000


@permission_classes([permissions.IsAdminUser])
class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@permission_classes([permissions.IsAdminUser])
class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


@permission_classes([permissions.AllowAny])
class FoodgramUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = MyPaginator

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    @action(['get'],
            detail=False,
            url_path='me',
            )
    def me(self, request):
        user = request.user
        serializer = FollowSerializer(user)
        return Response(serializer.data)

    @action(['get'],
            detail=False,
            url_path='subscriptions',
            )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(['post'],
            detail=False,
            permission_classes=permissions.IsAuthenticated
            )
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'],
            detail=True,
            url_path='subscribe',
            permission_classes=permissions.IsAuthenticated
            )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        follow, _ = Follow.objects.get_or_create(author=author, user=user)

        if request.method == 'POST':
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(detail=False,
            permission_classes=permissions.IsAuthenticated
            )
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['post', 'delete'],
            detail=True,
            url_path='favorite',
            permission_classes=permissions.IsAuthenticated
            )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite, _ = Favorite.objects.get_or_create(recipe=recipe, user=user)

        if request.method == 'POST':
            serializer = SmallReadRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'],
            detail=True,
            url_path='shopping_cart',
            permission_classes=permissions.IsAuthenticated
            )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart, _ = ShoppingCart.objects.get_or_create(
            recipe=recipe, user=user)

        if request.method == 'POST':
            serializer = SmallReadRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
