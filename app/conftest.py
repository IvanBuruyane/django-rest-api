import pytest
from django.contrib.auth import get_user_model
from helpers.test_helpers import create_user


@pytest.fixture(scope="function")
def setup_admin(client):
    admin_user = get_user_model().objects.create_superuser(
        email="admin@londonappdev.com", password="123"
    )
    client.force_login(admin_user)
    user = get_user_model().objects.create_user(
        email="test_user@londonappdev.com", password="123", name="Test User"
    )
    return {"admin_user": admin_user, "user": user}


# @pytest.fixture(scope="function")
# def create_and_authenticate_user(client):
#     user = create_user(
#         email="test@londonappdev.com",
#         password="testpass",
#         name="name",
#     )
#     client.login(username="test@londonappdev.com", password="testpass")
#
#
#     return user
