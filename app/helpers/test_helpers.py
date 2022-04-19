import random
import string
from typing import Any, List, Tuple

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient

from core.models import User


def random_string(chars=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(chars) for _ in range(n))


def create_user(**params) -> User:
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


def create_and_authenticate_user() -> Tuple[User, APIClient]:
    user = create_user(
        email="test@londonappdev.com",
        password="testpass",
        name="name",
    )
    client = APIClient()
    client.force_authenticate(user)

    return user, client


def create_sample_recipe(user: User, **params) -> Recipe:
    """Create and return a sample recipe"""
    defaults = {
        "title": "Sample recipe",
        "minutes_to_cook": 10,
        "price": 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user: User, name: str = "Main course") -> Tag:
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user: User, name: str = "Cinnamon") -> Ingredient:
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def create_param_value_pairs(param: str, values: List) -> List:
    return list(map(lambda el: (param, el), values))
