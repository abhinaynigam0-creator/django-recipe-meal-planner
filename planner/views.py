from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import IngredientFormSet, PlannedMealForm, RecipeForm, SignUpForm
from .models import PlannedMeal, Recipe


def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect("planner")
    return render(request, "registration/signup.html", {"form": form})


# ---------- Recipes ----------
@login_required
def recipe_list(request):
    q = request.GET.get("q", "")
    recipes = Recipe.objects.filter(owner=request.user)
    if q:
        # search in title OR in ingredient names
        from django.db.models import Q
        recipes = recipes.filter(Q(title__icontains=q) | Q(ingredients__name__icontains=q)).distinct()
    return render(request, "planner/recipe_list.html", {"recipes": recipes, "q": q})


@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    return render(request, "planner/recipe_detail.html", {"recipe": recipe})


def _save_recipe(request, recipe, title):
    form = RecipeForm(request.POST or None, instance=recipe)
    formset = IngredientFormSet(request.POST or None, instance=recipe)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        saved = form.save(commit=False)
        saved.owner = request.user
        saved.save()
        formset.instance = saved
        formset.save()
        return redirect("recipe_detail", pk=saved.pk)
    return render(request, "planner/recipe_form.html", {"form": form, "formset": formset, "title": title})


@login_required
def recipe_create(request):
    return _save_recipe(request, Recipe(owner=request.user), "New recipe")


@login_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    return _save_recipe(request, recipe, "Edit recipe")


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    if request.method == "POST":
        recipe.delete()
        return redirect("recipe_list")
    return render(request, "planner/recipe_confirm_delete.html", {"recipe": recipe})


# ---------- Weekly planner ----------
def _week_start(request):
    """Monday of the week given by ?week=YYYY-MM-DD (default: this week)."""
    try:
        d = date.fromisoformat(request.GET.get("week", ""))
    except ValueError:
        d = timezone.localdate()
    return d - timedelta(days=d.weekday())


@login_required
def planner(request):
    start = _week_start(request)
    days = [start + timedelta(days=i) for i in range(7)]
    meals = PlannedMeal.objects.filter(owner=request.user, date__range=(days[0], days[-1])).select_related("recipe")
    grid = defaultdict(lambda: defaultdict(list))
    for m in meals:
        grid[m.date][m.meal_type].append(m)
    rows = [{"date": d, "slots": [(key, label, grid[d][key]) for key, label in PlannedMeal.MEAL_TYPES]}
            for d in days]
    return render(request, "planner/planner.html", {
        "rows": rows, "start": start, "end": days[-1], "today": timezone.localdate(),
        "prev": start - timedelta(days=7), "next": start + timedelta(days=7)})


@login_required
def meal_add(request):
    initial = {k: request.GET[k] for k in ("date", "meal_type") if k in request.GET}
    form = PlannedMealForm(request.POST or None, user=request.user, initial=initial)
    if form.is_valid():
        meal = form.save(commit=False)
        meal.owner = request.user
        meal.save()
        return redirect(f"/?week={meal.date - timedelta(days=meal.date.weekday())}")
    return render(request, "planner/meal_form.html", {"form": form})


@login_required
def meal_delete(request, pk):
    meal = get_object_or_404(PlannedMeal, pk=pk, owner=request.user)
    week = meal.date - timedelta(days=meal.date.weekday())
    if request.method == "POST":
        meal.delete()
    return redirect(f"/?week={week}")


# ---------- Shopping list ----------
@login_required
def shopping_list(request):
    start = _week_start(request)
    end = start + timedelta(days=6)
    meals = PlannedMeal.objects.filter(owner=request.user, date__range=(start, end)).select_related("recipe")
    totals = defaultdict(Decimal)
    for m in meals:
        scale = Decimal(m.servings) / Decimal(m.recipe.servings or 1)   # scale recipe to planned servings
        for ing in m.recipe.ingredients.all():
            totals[(ing.name.strip().lower(), ing.unit)] += ing.quantity * scale
    items = sorted(({"name": n.title(), "unit": u, "qty": q} for (n, u), q in totals.items()),
                   key=lambda i: i["name"])
    return render(request, "planner/shopping_list.html", {
        "items": items, "start": start, "end": end, "meal_count": meals.count(),
        "prev": start - timedelta(days=7), "next": start + timedelta(days=7)})
