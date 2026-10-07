from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from planner.models import Ingredient, PlannedMeal, Recipe

RECIPES = {
    "Veg Omelette": ("Quick protein-rich breakfast", 1, 5, 7, "Beat eggs with salt. Saute onion and tomato, pour eggs, cook until set.",
        [("Eggs", 3, "pcs"), ("Onion", 0.5, "pcs"), ("Tomato", 1, "pcs"), ("Butter", 1, "tsp")]),
    "Masala Oats": ("Savoury oats bowl", 1, 5, 10, "Roast oats, saute veggies with spices, add water and cook until soft.",
        [("Oats", 50, "g"), ("Onion", 0.5, "pcs"), ("Carrot", 1, "pcs"), ("Water", 250, "ml")]),
    "Chicken Fried Rice": ("Weeknight dinner favourite", 2, 15, 20, "Cook rice and cool it. Stir-fry chicken, veggies and eggs, add rice and soy sauce.",
        [("Rice", 200, "g"), ("Chicken", 250, "g"), ("Eggs", 2, "pcs"), ("Onion", 1, "pcs"), ("Carrot", 1, "pcs"), ("Soy Sauce", 2, "tbsp")]),
    "Paneer Butter Masala": ("Rich creamy curry", 2, 15, 25, "Fry paneer. Make a tomato-butter gravy, add cream and paneer, simmer.",
        [("Paneer", 250, "g"), ("Tomato", 4, "pcs"), ("Onion", 1, "pcs"), ("Butter", 2, "tbsp"), ("Cream", 100, "ml")]),
    "Dal Tadka with Rice": ("Comfort food", 2, 10, 30, "Pressure cook dal. Prepare tadka with cumin, garlic, onion, tomato and mix in.",
        [("Toor Dal", 150, "g"), ("Rice", 200, "g"), ("Onion", 1, "pcs"), ("Tomato", 2, "pcs"), ("Garlic", 4, "pcs")]),
    "Greek Salad": ("Light lunch", 2, 10, 0, "Chop everything, toss with olive oil and oregano.",
        [("Cucumber", 2, "pcs"), ("Tomato", 3, "pcs"), ("Onion", 1, "pcs"), ("Feta Cheese", 100, "g"), ("Olive Oil", 2, "tbsp")]),
    "Pasta Arrabbiata": ("Spicy tomato pasta", 2, 10, 20, "Boil pasta. Simmer garlic, chilli and tomatoes into a sauce, toss together.",
        [("Pasta", 200, "g"), ("Tomato", 4, "pcs"), ("Garlic", 3, "pcs"), ("Olive Oil", 2, "tbsp")]),
    "Fruit Yogurt Bowl": ("Easy snack", 1, 5, 0, "Top yogurt with chopped fruit and honey.",
        [("Yogurt", 200, "g"), ("Banana", 1, "pcs"), ("Honey", 1, "tsp")]),
}

# (weekday 0=Mon, meal type, recipe, servings)
PLAN = [(0, "breakfast", "Veg Omelette", 2), (0, "dinner", "Dal Tadka with Rice", 2),
        (1, "breakfast", "Masala Oats", 1), (1, "lunch", "Greek Salad", 2), (1, "dinner", "Chicken Fried Rice", 4),
        (2, "breakfast", "Veg Omelette", 2), (2, "dinner", "Pasta Arrabbiata", 2),
        (3, "lunch", "Greek Salad", 2), (3, "dinner", "Paneer Butter Masala", 2), (3, "snack", "Fruit Yogurt Bowl", 1),
        (4, "breakfast", "Masala Oats", 1), (4, "dinner", "Chicken Fried Rice", 2),
        (5, "lunch", "Dal Tadka with Rice", 4), (5, "dinner", "Paneer Butter Masala", 4),
        (6, "breakfast", "Veg Omelette", 2), (6, "snack", "Fruit Yogurt Bowl", 2)]


class Command(BaseCommand):
    help = "Create demo user (demo / demo12345) with recipes and a meal plan for the current week"

    def handle(self, *args, **opts):
        user, _ = User.objects.get_or_create(username="demo")
        user.set_password("demo12345")
        user.save()
        Recipe.objects.filter(owner=user).delete()
        recipes = {}
        for title, (desc, servings, prep, cook, steps, ings) in RECIPES.items():
            r = Recipe.objects.create(owner=user, title=title, description=desc, servings=servings,
                                      prep_minutes=prep, cook_minutes=cook, instructions=steps)
            Ingredient.objects.bulk_create([Ingredient(recipe=r, name=n, quantity=q, unit=u) for n, q, u in ings])
            recipes[title] = r
        today = timezone.localdate()
        monday = today - timedelta(days=today.weekday())
        for wd, meal, title, serv in PLAN:
            PlannedMeal.objects.create(owner=user, recipe=recipes[title], meal_type=meal,
                                       date=monday + timedelta(days=wd), servings=serv)
        self.stdout.write(self.style.SUCCESS("Seeded 8 recipes + weekly plan. Login: demo / demo12345"))
