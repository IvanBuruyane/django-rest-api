import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from test_data import TestData
from helpers.test_helpers import random_string

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


@pytest.mark.django_db
class TestPublicUserAPI:
    """Test the users API (public)"""

    def test_create_valid_user_success(self, client):
        """Test creating using with a valid payload is successful"""
        payload = {
            "email": "test@londonappdev.com",
            "password": "testpass",
            "name": "name",
        }
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        user = get_user_model().objects.get(**res.data)
        assert user.check_password(payload["password"]) is True
        assert "password" not in res.data

    def test_user_exists(self, client):
        """Test creating a user that already exists fails"""
        payload = {
            "email": "test@londonappdev.com",
            "password": "testpass",
            "name": "name",
        }
        create_user(**payload)
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "param, value",
        list(map(lambda el: ("email", el), TestData.INVALID_EMAILS))
        + list(map(lambda el: ("password", el), ["pwfs", "", None]))
        + list(map(lambda el: ("name", el), ["fn", "", None, random_string(n=256)])),
    )
    def test_create_user_with_invalid_parameter_should_fail(self, client, param, value):
        email = "test_invalid_param@londonappdev.com"
        payload = {
            "email": email,
            "password": "testpass",
            "name": "name",
            param: value,
        }
        if value is None:
            payload.pop(param)
        res = client.post(CREATE_USER_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        user_exists = get_user_model().objects.filter(email=email).exists()
        assert user_exists is False

    def test_create_token_for_user(self, client):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@londonappdev.com",
            "password": "testpass",
            "name": "test_user",
        }
        create_user(**payload)
        res = client.post(TOKEN_URL, payload)

        assert "token" in res.data
        assert res.status_code == status.HTTP_200_OK

    def test_create_token_invalid_credentials(self, client):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="test@londonappdev.com", password="testpass")
        payload = {"email": "test@londonappdev.com", "password": "wrong"}
        res = client.post(TOKEN_URL, payload)

        assert "token" not in res.data
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_token_for_non_existing_user(self, client):
        """Test that token is not created if user doens't exist"""
        payload = {"email": "test@londonappdev.com", "password": "testpass"}
        res = client.post(TOKEN_URL, payload)

        assert "token" not in res.data
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("param", ["email", "password"])
    def test_create_token_without_parameter(self, client, param):
        """Test that email and password are required"""
        payload = {"email": "test@londonappdev.com", "password": "testpass"}
        create_user(**payload)
        payload.pop(param)
        res = client.post(TOKEN_URL, payload)

        assert "token" not in res.data
        assert res.status_code == status.HTTP_400_BAD_REQUEST
