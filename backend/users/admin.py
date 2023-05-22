from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser
from .forms import FoodgramChangeForm, FoodgramUserCreationForm


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    add_form = FoodgramUserCreationForm
    form = FoodgramChangeForm
    model = FoodgramUser
    list_filter = ('email', 'first_name')
    list_display = [
        'id', 'email', 'username', 'first_name', 'last_name',
        ]
