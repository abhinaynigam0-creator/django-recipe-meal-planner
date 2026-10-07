from django.urls import path
from . import views

urlpatterns = [
    path("", views.planner, name="planner"),
    path("signup/", views.signup, name="signup"),
    path("meal/add/", views.meal_add, name="meal_add"),
    path("meal/<int:pk>/delete/", views.meal_delete, name="meal_delete"),
    path("shopping-list/", views.shopping_list, name="shopping_list"),
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("recipes/new/", views.recipe_create, name="recipe_create"),
    path("recipes/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/<int:pk>/edit/", views.recipe_update, name="recipe_update"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
]
