from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Ingredient, PlannedMeal, Recipe


class BaseCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user("a", password="pw12345678")
        self.u2 = User.objects.create_user("b", password="pw12345678")
        self.r = Recipe.objects.create(owner=self.u1, title="Pasta", instructions="Boil", servings=2)
        Ingredient.objects.create(recipe=self.r, name="Tomato", quantity=4, unit="pcs")
        Ingredient.objects.create(recipe=self.r, name="Pasta", quantity=200, unit="g")


class ShoppingListTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="a", password="pw12345678")
        self.week = "2026-10-05"  # a Monday

    def test_scaling_and_merging(self):
        # 4 servings of a 2-serving recipe -> x2, plus another 2-serving meal -> x1 => x3 total
        PlannedMeal.objects.create(owner=self.u1, recipe=self.r, date=date(2026, 10, 5), servings=4)
        PlannedMeal.objects.create(owner=self.u1, recipe=self.r, date=date(2026, 10, 7), servings=2)
        resp = self.client.get(reverse("shopping_list") + f"?week={self.week}")
        items = {i["name"]: i["qty"] for i in resp.context["items"]}
        self.assertEqual(items["Tomato"], Decimal("12"))
        self.assertEqual(items["Pasta"], Decimal("600"))

    def test_other_week_not_included(self):
        PlannedMeal.objects.create(owner=self.u1, recipe=self.r, date=date(2026, 10, 14), servings=2)
        resp = self.client.get(reverse("shopping_list") + f"?week={self.week}")
        self.assertEqual(resp.context["items"], [])


class ViewTests(BaseCase):
    def test_login_required(self):
        self.assertEqual(self.client.get(reverse("planner")).status_code, 302)

    def test_cannot_view_others_recipe(self):
        self.client.login(username="b", password="pw12345678")
        self.assertEqual(self.client.get(reverse("recipe_detail", args=[self.r.pk])).status_code, 404)

    def test_create_recipe_with_ingredients(self):
        self.client.login(username="a", password="pw12345678")
        data = {"title": "Toast", "description": "", "servings": 1, "prep_minutes": 1, "cook_minutes": 2,
                "instructions": "Toast it",
                "ingredients-TOTAL_FORMS": 1, "ingredients-INITIAL_FORMS": 0,
                "ingredients-MIN_NUM_FORMS": 0, "ingredients-MAX_NUM_FORMS": 1000,
                "ingredients-0-name": "Bread", "ingredients-0-quantity": "2", "ingredients-0-unit": "pcs"}
        self.client.post(reverse("recipe_create"), data)
        toast = Recipe.objects.get(title="Toast")
        self.assertEqual(toast.owner, self.u1)
        self.assertEqual(toast.ingredients.count(), 1)

    def test_plan_a_meal(self):
        self.client.login(username="a", password="pw12345678")
        self.client.post(reverse("meal_add"), {"recipe": self.r.pk, "date": "2026-10-06",
                                               "meal_type": "dinner", "servings": 2})
        self.assertEqual(PlannedMeal.objects.filter(owner=self.u1).count(), 1)
