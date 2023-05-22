from django.contrib import admin
from .models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Follow, ShoppingCart, Favorite
    )


admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    filter_horizontal = ['tags', 'ingredients']
    list_display = ['author', 'name', ]
    list_filter = ['author', 'name', 'tags']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = ['name', 'measurement_unit', ]
