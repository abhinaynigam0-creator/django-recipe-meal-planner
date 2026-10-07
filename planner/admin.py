from django.contrib import admin
from .models import Ingredient, PlannedMeal, Recipe


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "servings", "prep_minutes", "cook_minutes")
    search_fields = ("title",)
    inlines = [IngredientInline]


@admin.register(PlannedMeal)
class PlannedMealAdmin(admin.ModelAdmin):
    list_display = ("recipe", "owner", "date", "meal_type", "servings")
    list_filter = ("meal_type", "date")
