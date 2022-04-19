import random
import string
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient


def random_string(chars=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(chars) for _ in range(n))


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


def create_and_authenticate_user():
    user = create_user(
        email="test@londonappdev.com",
        password="testpass",
        name="name",
    )
    client = APIClient()
    client.force_authenticate(user)

    return user, client


def create_sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        "title": "Sample recipe",
        "minutes_to_cook": 10,
        "price": 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user, name="Main course"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name="Cinnamon"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)
