import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from test_data import TestData
from helpers.test_helpers import create_user
from core import models
from unittest.mock import patch


@pytest.mark.django_db
class TestModels:
    def test_create_user_with_email_successful(self) -> None:
        """Test creating a new user with an email is successful"""
        email = "test@londonappdev.com"
        password = "Password123"
        user = get_user_model().objects.create_user(email=email, password=password)
        assert user.email == email
        assert user.check_password(password) is True

    def test_new_user_email_normalized(self) -> None:
        """Test the email for a new user is normalized"""
        email = "test@LonDOnaPPDev.cOm"
        user = get_user_model().objects.create_user(email=email, password="123")
        assert user.email == email.lower()

    @pytest.mark.parametrize("invalid_email", TestData.INVALID_EMAILS)
    def test_new_user_invalid_email(self, invalid_email: str) -> None:
        """Test creating user with empty email raises error"""
        with pytest.raises(ValidationError):
            get_user_model().objects.create_user(email=invalid_email, password="123")

    def test_super_user_can_be_created(self) -> None:
        """Test creating a superuser"""
        superuser = get_user_model().objects.create_superuser(
            email="superuser@londonappdev.com", password="123"
        )
        assert superuser.is_superuser is True
        assert superuser.is_staff is True

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=create_user(email="test@londonappdev.com", password="123456"),
            name="Vegan",
        )

        assert str(tag) == tag.name

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=create_user(email="test@londonappdev.com", password="123456"),
            name="Cucumber",
        )

        assert str(ingredient) == ingredient.name

    def test_recipe_str(self):
        """Test the ingredient string representation"""
        recipe = models.Recipe.objects.create(
            user=create_user(email="test@londonappdev.com", password="123456"),
            title="Steak and mushroom sauce",
            minutes_to_cook=5,
            price=5.00,
        )

        assert str(recipe) == recipe.title

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "myimage.jpg")

        exp_path = f"uploads/recipe/{uuid}.jpg"
        assert file_path == exp_path
