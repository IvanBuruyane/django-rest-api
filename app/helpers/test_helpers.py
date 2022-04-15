import random
import string
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


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
