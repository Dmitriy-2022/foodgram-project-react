from django.contrib import admin
from .models import Recipe, Tag, Ingredient, RecipeIngredient


admin.site.register(Tag)
admin.site.register(RecipeIngredient)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    filter_horizontal = ['tags', 'ingredients']
    list_display = [
        'id', 'author', 'name', ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    # filter_horizontal = ['id', 'ingredients']
