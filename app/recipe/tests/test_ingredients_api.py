import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


from core.models import Ingredient
from helpers.test_helpers import create_and_authenticate_user, random_string

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


@pytest.mark.django_db(reset_sequences=True)
class TestsPrivateIngredientsAPI:
    """Test ingredients can be retrieved by authorized user"""

    @pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
    def test_login_required(self, client, method):
        """Test that login is required to access this endpoint"""
        if method == "get":
            res = client.get(INGREDIENTS_URL)
        elif method == "post":
            res = client.post(INGREDIENTS_URL)
        elif method == "put":
            res = client.put(reverse("recipe:ingredient-detail", kwargs={"pk": "1"}))
        elif method == "delete":
            res = client.delete(reverse("recipe:ingredient-detail", kwargs={"pk": "1"}))

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

    def test_retrieve_one_ingredient(self):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Cucumber")
        Ingredient.objects.create(user=user, name="Potato")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": "2"})

        res = client.get(url)

        ingredient = Ingredient.objects.get(pk=2)
        serializer = IngredientSerializer(ingredient)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_retrieve_non_existent_ingredient(self, value):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Vegan")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": value})

        res = client.get(url)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_create_ingredient_successful(self):
        """Test creating a new tag"""
        user, client = create_and_authenticate_user()
        payload = {"name": "Potato"}
        client.post(INGREDIENTS_URL, payload, format="json")

        exists = Ingredient.objects.filter(user=user, name=payload["name"]).exists()
        assert exists is True

    @pytest.mark.parametrize("name", ["", None, random_string(n=256)])
    def test_create_ingredient_invalid(self, name):
        """Test creating a new tag with invalid payload"""
        user, client = create_and_authenticate_user()
        payload = {"name": name}
        if not name:
            payload.pop("name")
        res = client.post(INGREDIENTS_URL, payload, format="json")

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_ingredient_successful(self):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Cucumber")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": 1})
        res = client.put(url, {"name": "updated_cucumber"})
        serializer = IngredientSerializer(Ingredient.objects.get(id=1))

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_update_non_existent_ingredient(self, value):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Cucumber")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": value})
        res = client.put(url, {"name": "updated_cucumber"})
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "payload",
        [{"name": ""}, {}, {"name": random_string(n=256)}, {"incorrect_key": "value"}],
    )
    def test_update_ingredient_incorrect_payload(self, payload):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Cucumber")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": 1})
        res = client.put(url, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_ingredient_successful(self):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Ingredient.objects.create(user=user, name="Vegan")
        url = reverse("recipe:ingredient-detail", kwargs={"pk": 1})
        res = client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert client.get(url).status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_delete_non_existent_ingredient(self, value):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        url = reverse("recipe:tag-detail", kwargs={"pk": value})
        res = client.delete(url)

        assert res.status_code == status.HTTP_404_NOT_FOUND
