from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import FoodgramUser


class FoodgramUserCreationForm(UserCreationForm):

    class Meta:
        model = FoodgramUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class FoodgramChangeForm(UserChangeForm):

    class Meta:
        model = FoodgramUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
