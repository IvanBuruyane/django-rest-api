import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from helpers.test_helpers import (
    create_and_authenticate_user,
    create_sample_recipe,
    create_sample_tag,
    create_sample_ingredient,
)


RECIPES_URL = reverse("recipe:recipe-list")


@pytest.mark.django_db(reset_sequences=True)
class TestsPrivateRecipeApi:
    """Test authenticated recipe API access"""

    def test_required_auth(self, client):
        """Test the authenticaiton is required"""
        res = client.get(RECIPES_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        create_sample_recipe(user=user, title="Sample recipe 2")

        res = client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user, client = create_and_authenticate_user()
        user2 = get_user_model().objects.create_user(
            "other@londonappdev.com", "password123"
        )
        create_sample_recipe(user=user2, title="User2 sample recipe")
        create_sample_recipe(user=user)

        res = client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=user)
        serializer = RecipeSerializer(recipes, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data == serializer.data

    def test_retrieve_one_recipe(self):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user, title="First_recipe")
        recipe2 = create_sample_recipe(user=user, title="Second_recipe")
        recipe2.tags.add(create_sample_tag(user=user))
        recipe2.ingredients.add(create_sample_ingredient(user=user))
        recipe2.ingredients.add(create_sample_ingredient(user=user, name="Cucumber"))
        url = reverse("recipe:recipe-detail", kwargs={"pk": "2"})
        res = client.get(url)

        recipe = Recipe.objects.get(pk=2)
        serializer = RecipeDetailSerializer(recipe)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_retrieve_non_existent_tag(self, value):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        url = reverse("recipe:recipe-detail", kwargs={"pk": value})

        res = client.get(url)
        assert res.status_code == status.HTTP_404_NOT_FOUND
