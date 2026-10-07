from django.conf import settings
from django.db import models


class Recipe(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    instructions = models.TextField()
    servings = models.PositiveIntegerField(default=2)
    prep_minutes = models.PositiveIntegerField(default=10)
    cook_minutes = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def total_minutes(self):
        return self.prep_minutes + self.cook_minutes


class Ingredient(models.Model):
    UNIT_CHOICES = [("g", "g"), ("kg", "kg"), ("ml", "ml"), ("l", "l"), ("tsp", "tsp"),
                    ("tbsp", "tbsp"), ("cup", "cup"), ("pcs", "pcs")]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="pcs")

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"


class PlannedMeal(models.Model):
    MEAL_TYPES = [("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner"), ("snack", "Snack")]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="planned_meals")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="planned")
    date = models.DateField()
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES, default="dinner")
    servings = models.PositiveIntegerField(default=2)

    class Meta:
        ordering = ["date", "meal_type"]

    def __str__(self):
        return f"{self.recipe} on {self.date} ({self.meal_type})"
