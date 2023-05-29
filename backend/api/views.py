from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser import views
from django.shortcuts import get_object_or_404

from api.permissions import IsAdminAuthorOrReadOnly
from recipes.models import (
    Tag, Recipe, Ingredient,
    Follow, Favorite, ShoppingCart,
    RecipeIngredient
    )
from .serializers import (
    SmallReadRecipeSerializer, ReadRecipeSerializer,
    UsersSerializer, PasswordSerializer, TagSerializer,
    CreateUpdateRecipeSerializer, IngredientSerializer, FollowSerializer
    )


User = get_user_model()
SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


@permission_classes([permissions.AllowAny])
class FoodgramUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

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
    permission_classes = (IsAdminAuthorOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return CreateUpdateRecipeSerializer

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

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
