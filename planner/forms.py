from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

from .models import Ingredient, PlannedMeal, Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "description", "servings", "prep_minutes", "cook_minutes", "instructions"]
        widgets = {"instructions": forms.Textarea(attrs={"rows": 5})}


IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient, fields=["name", "quantity", "unit"], extra=3, can_delete=True)


class PlannedMealForm(forms.ModelForm):
    class Meta:
        model = PlannedMeal
        fields = ["recipe", "date", "meal_type", "servings"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipe"].queryset = Recipe.objects.filter(owner=user)  # own recipes only


class SignUpForm(UserCreationForm):
    pass
