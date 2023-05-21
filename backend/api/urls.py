from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodgramUserViewSet, TagsViewSet, RecipesViewSet, IngredientsViewSet


app_name = 'api'

router = DefaultRouter()
router.register('users', FoodgramUserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes/(?P<recipe_id>.+)', RecipesViewSet, basename='favorite')
router.register(r'users/(?P<user_id>.+)', FoodgramUserViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]