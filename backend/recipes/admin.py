from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Follow, ShoppingCart, Favorite
    )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    filter_horizontal = ['tags', 'ingredients']
    list_display = ['author', 'name', 'get_favorites']
    list_filter = ['author', 'name', 'tags']

    def get_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    get_favorites.short_description = 'Добавили в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name']
    list_filter = ['name']


admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
