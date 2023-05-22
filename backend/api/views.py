from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import filters, permissions, status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from djoser import views
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import io
from django.http import FileResponse

from recipes.models import RecipeIngredient, Tag, Recipe, Ingredient, Follow, Favorite, ShoppingCart
from .serializers import SmallReadRecipeSerializer, ReadRecipeSerializer, UsersSerializer, PasswordSerializer, TagSerializer, CreateUpdateRecipeSerializer, IngredientSerializer, FollowSerializer

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
        subscriptions = User.objects.filter(following__user=request.user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(['post'],
            detail=False,
            permission_classes=permissions.IsAuthenticated
            )
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data["new_password"])
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
        else:
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

    @action(['get'],
            detail=False,
            url_path='download_shopping_cart',
            )
    # def download_shopping_cart(self, request):
    #     # response = HttpResponse(content_type='application/pdf')
    #     # response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
    #     # p = canvas.Canvas(response) 
    #     # p.setFont("Times-Roman", 55) 
    #     # p.drawString(100, 700, "Hello, Javatpoint.")
    #     # p.showPage()
    #     # p.save()
    #     # return response



    #     user = User.objects.filter(id=1)
    #     # if not user.buylist.exists():
    #     #     return Response(status=status.HTTP_400_BAD_REQUEST)
    #     buylist = {}
    #     ingredients = RecipeIngredient.objects.filter(recipe__shopping_cart__user=1).values_list(
    #         'ingredient__name', 'ingredient__measurement_unit',
    #         'amount',
    #         )

    #     for item in ingredients:
    #         name = item[0]
    #         if name not in buylist:
    #             buylist[name] = {
    #                 'measurement_unit': item[1],
    #                 'amount': item[2]
    #             }
    #         else:
    #             buylist[name]['amount'] += item[2]


    #     buffer = io.BytesIO()

    #     file = canvas.Canvas(buffer)
    #     file.setFont("Times-Roman", 14)
    #     file.drawString(100, 700, "Список покупок")
    #     file.showPage()
    #     file.save()
    #     buffer.seek(0)
    #     return FileResponse(
    #         buffer,
    #         as_attachment=True,
    #         filename='shopping_cart.pdf'
    #     )
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
            serializer = SmallReadRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
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
        shopping_cart, _ = ShoppingCart.objects.get_or_create(recipe=recipe, user=user)

        if request.method == 'POST':
            serializer = SmallReadRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
