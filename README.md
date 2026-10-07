# Recipe Meal Planner (Django)

A multi-user web app to store recipes, plan meals for the week, and auto-generate a shopping list.
Based on the *Recipe Meal Planner* project from the
[GeeksforGeeks Django Projects](https://www.geeksforgeeks.org/python/django-projects/) list.

## Features
- Sign up / login / logout (Django auth)
- Recipes: create, edit, delete, with multiple ingredients (inline formset) and prep/cook time
- Search recipes by title **or ingredient name**
- Weekly planner: 7 days x (breakfast, lunch, dinner, snack), with previous/next week navigation
- Plan a meal with a chosen number of servings
- **Shopping list** for any week: merges identical ingredients and scales quantities to planned servings
- Per-user data isolation, Django admin, unit tests, seed command with demo data

## Tech
Python 3.10+, Django 5+, SQLite, plain HTML/CSS.

## Run it
```bash
git clone <your-repo-url> && cd recipe-meal-planner
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data        # 8 recipes + this week's plan; login demo / demo12345
python manage.py runserver
```
Open http://127.0.0.1:8000/ . Tests: `python manage.py test`

## Structure
```
config/                       settings, root urls
planner/models.py             Recipe, Ingredient, PlannedMeal
planner/views.py              recipes CRUD, weekly planner, meal add/delete, shopping list
planner/forms.py              RecipeForm, IngredientFormSet, PlannedMealForm
planner/management/commands/  seed_data
planner/tests.py              shopping-list maths, permissions, formset save
templates/                    base, planner/recipe pages, login/signup
```

## How it works
- **Models:** `Recipe` -> many `Ingredient` (ForeignKey). `PlannedMeal` links a user, a recipe, a date, a meal type and servings.
- **Weekly grid:** the view finds the Monday of `?week=`, loads that week's meals and groups them by date and meal type.
- **Shopping list:** for each planned meal, `scale = planned servings / recipe servings`; each ingredient quantity
  x scale is summed in a dict keyed by (name, unit). Example: Chicken Fried Rice (serves 2) planned for 4 -> all quantities x2.
- **Ingredient formset:** `inlineformset_factory` lets one page save a recipe and its ingredients together.
- **Security:** `@login_required`, `get_object_or_404(..., owner=request.user)`, forms only offer the user's own recipes, CSRF tokens, POST-only deletes.

## Demo account
- demo/demo12345