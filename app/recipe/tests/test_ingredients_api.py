import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


from core.models import Ingredient
from helpers.test_helpers import create_and_authenticate_user, random_string

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


@pytest.mark.django_db
class TestsPrivateIngredientsAPI:
    """Test ingredients can be retrieved by authorized user"""

    def test_login_required(self, client):
        """Test that login is required to access this endpoint"""
        res = client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="kale")
        Ingredient.objects.create(user=user, name="Salt")

        res = client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user, client = create_and_authenticate_user()
        user2 = get_user_model().objects.create_user(
            "other@londonappdev.com", "testpass"
        )
        Ingredient.objects.create(user=user2, name="Vinegar")

        ingredient = Ingredient.objects.create(user=user, name="Tumeric")

        res = client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["name"] == ingredient.name

    def test_create_ingredient_successful(self):
        """Test creating a new tag"""
        user, client = create_and_authenticate_user()
        payload = {"name": "Potato"}
        client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(user=user, name=payload["name"]).exists()
        assert exists is True

    @pytest.mark.parametrize("name", ["", None, random_string(n=256)])
    def test_create_tag_invalid(self, name):
        """Test creating a new tag with invalid payload"""
        user, client = create_and_authenticate_user()
        payload = {"name": name}
        if not name:
            payload.pop("name")
        res = client.post(INGREDIENTS_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST
