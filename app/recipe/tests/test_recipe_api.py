import pytest
import os
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
    create_param_value_pairs,
    random_string,
    add_image_to_the_recipe,
)


RECIPES_URL = reverse("recipe:recipe-list")
INVALID_PARAMS = (
    create_param_value_pairs("title", ["", None, random_string(n=256), True])
    + create_param_value_pairs("minutes_to_cook", ["", None, "dfadf", 3424.3434, False])
    + create_param_value_pairs(
        "price", ["", None, "afadfa", False, 1.122141242141, 12345678921]
    )
    + create_param_value_pairs(
        "tags", ["", None, 1232, "adfadf", True, [1], ["dafad"], [None], [True]]
    )
    + create_param_value_pairs(
        "ingredients",
        ["", None, 1232, "adfadf", True, [1], ["dafad"], [None], [True]],
    )
    + create_param_value_pairs("link", [12312, "akfjabfa", True, random_string(n=256)])
)


@pytest.mark.django_db(reset_sequences=True)
class TestsPrivateRecipeApi:
    """Test authenticated recipe API access"""

    @pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
    def test_login_required(self, client, method):
        """Test that login is required to access this endpoint"""
        if method == "get":
            res = client.get(RECIPES_URL)
        elif method == "post":
            res = client.post(RECIPES_URL)
        elif method == "put":
            res = client.put(reverse("recipe:recipe-detail", kwargs={"pk": "1"}))
        elif method == "delete":
            res = client.delete(reverse("recipe:recipe-detail", kwargs={"pk": "1"}))

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
        """Test retrieving recipe"""
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
    def test_retrieve_non_existent_recipe(self, value):
        """Test retrieving recipe"""
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        url = reverse("recipe:recipe-detail", kwargs={"pk": value})

        res = client.get(url)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        user, client = create_and_authenticate_user()
        payload = {
            "title": "Chocolate cheesecake",
            "minutes_to_cook": 30,
            "price": 5.00,
            "tags": [],
            "ingredients": [],
        }
        res = client.post(RECIPES_URL, payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED, res.data
        recipe = Recipe.objects.get(id=res.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        assert res.data == serializer.data

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        user, client = create_and_authenticate_user()
        tag1 = create_sample_tag(user=user, name="Vegan")
        tag2 = create_sample_tag(user=user, name="Dessert")
        payload = {
            "title": "Avocado lime cheesecake",
            "tags": [tag1.id, tag2.id],
            "ingredients": [],
            "minutes_to_cook": 60,
            "price": 20.00,
            "link": "https://www.youtube.com",
        }
        res = client.post(RECIPES_URL, payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        recipe = Recipe.objects.get(id=res.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        assert res.data == serializer.data

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        user, client = create_and_authenticate_user()
        ingredient1 = create_sample_ingredient(user=user, name="Prawns")
        ingredient2 = create_sample_ingredient(user=user, name="Ginger")
        payload = {
            "title": "Thai prawn red curry",
            "ingredients": [ingredient1.id, ingredient2.id],
            "tags": [],
            "minutes_to_cook": 20,
            "price": 7.00,
        }

        res = client.post(RECIPES_URL, payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        recipe = Recipe.objects.get(id=res.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        assert res.data == serializer.data

    @pytest.mark.parametrize("param, value", INVALID_PARAMS)
    def test_create_recipe_with_invalid_params(self, param, value):
        user, client = create_and_authenticate_user()
        payload = {
            "title": "Chocolate cheesecake",
            "minutes_to_cook": 30,
            "price": 5.00,
            "tags": [],
            "ingredients": [],
        }
        if value is None:
            payload.pop(param)
        else:
            payload.update({param: value})
        res = client.post(RECIPES_URL, payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_recipe_success(self):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        ingredient1 = create_sample_ingredient(user=user, name="Prawns")
        ingredient2 = create_sample_ingredient(user=user, name="Ginger")
        tag1 = create_sample_tag(user=user, name="Supper")
        updated_payload = {
            "title": "Avocado lime cheesecake",
            "tags": [tag1.id],
            "ingredients": [ingredient1.id, ingredient2.id],
            "minutes_to_cook": 60,
            "price": 20.00,
            "link": "https://www.youtube.com",
        }
        url = reverse("recipe:recipe-detail", kwargs={"pk": 1})
        res = client.put(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_200_OK
        recipe = Recipe.objects.get(id=res.data["id"])
        recipe.refresh_from_db()
        serializer = RecipeDetailSerializer(recipe)
        assert res.data == serializer.data

    @pytest.mark.parametrize("param, value", INVALID_PARAMS)
    def test_update_recipe_with_invalid_params(self, param, value):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        updated_payload = {
            "title": "Chocolate cheesecake",
            "minutes_to_cook": 30,
            "price": 5.00,
            "tags": [],
            "ingredients": [],
        }
        if value is None:
            updated_payload.pop(param)
        else:
            updated_payload.update({param: value})
        url = reverse("recipe:recipe-detail", kwargs={"pk": 1})
        res = client.put(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_update_non_existent_recipe(self, value):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        updated_payload = {
            "title": "Chocolate cheesecake",
            "minutes_to_cook": 30,
            "price": 5.00,
            "tags": [],
            "ingredients": [],
        }
        url = reverse("recipe:recipe-detail", kwargs={"pk": value})
        res = client.put(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "param, value",
        [
            ("title", "New title"),
            ("minutes_to_cook", 30),
            ("price", 12.43),
            ("tags", []),
            ("ingredients", []),
            ("link", "https://www.youtube.com"),
        ],
    )
    def test_patch_recipe_success(self, param, value):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        if param == "tag":
            tag1 = create_sample_tag(user=user, name="Supper")
            value = [tag1.id]
        elif param == "ingredients":
            ingredient1 = create_sample_ingredient(user=user, name="Ginger")
            value = [ingredient1.id]
        updated_payload = {param: value}
        url = reverse("recipe:recipe-detail", kwargs={"pk": 1})
        res = client.patch(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_200_OK
        recipe = Recipe.objects.get(id=res.data["id"])
        recipe.refresh_from_db()
        serializer = RecipeDetailSerializer(recipe)
        assert res.data == serializer.data

    @pytest.mark.parametrize("param, value", INVALID_PARAMS)
    def test_patch_recipe_with_invalid_params(self, param, value):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        updated_payload = {}
        updated_payload.update({param: value})
        url = reverse("recipe:recipe-detail", kwargs={"pk": 1})
        res = client.patch(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_patch_non_existent_recipe(self, value):
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        updated_payload = {"title": "Chocolate cheesecake"}
        url = reverse("recipe:recipe-detail", kwargs={"pk": value})
        res = client.patch(url, updated_payload, format="json")
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_recipe_successful(self):
        """Test deleting existent recipe"""
        user, client = create_and_authenticate_user()
        create_sample_recipe(user=user)
        url = reverse("recipe:recipe-detail", kwargs={"pk": 1})
        res = client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert client.get(url).status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_delete_non_existent_recipe(self, value):
        """Test deleting non-existent recipe"""
        user, client = create_and_authenticate_user()
        url = reverse("recipe:recipe-detail", kwargs={"pk": value})
        res = client.delete(url)

        assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(reset_sequences=True)
class TestsRecipeImageUpload:
    @pytest.mark.parametrize(
        "image_ext",
        [
            "BMP",
            "DDS",
            "DIB",
            "EPS",
            "GIF",
            "ICNS",
            "IM",
            "JPEG",
            "PCX",
            "PNG",
            "PPM",
            "SGI",
            "SPIDER",
            "TGA",
            "TIFF",
            "WebP",
        ],
    )
    def test_upload_image_to_recipe(self, create_user_and_recipe, image_ext):
        """Test uploading an image to recipe"""
        user, client, recipe = create_user_and_recipe
        url = reverse("recipe:recipe-upload-image", args=[recipe.id])
        res = add_image_to_the_recipe(client, url, image_ext)

        recipe.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK, res.data
        assert "image" in res.data
        assert os.path.exists(recipe.image.path) is True

    def test_update_recipe_image(self, create_user_and_recipe):
        """Test uploading an image to recipe"""
        user, client, recipe = create_user_and_recipe
        url = reverse("recipe:recipe-upload-image", args=[recipe.id])
        add_image_to_the_recipe(client, url, "JPEG")
        recipe.refresh_from_db()
        res = add_image_to_the_recipe(client, url, "JPEG")
        recipe.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK, res.data
        assert "image" in res.data
        assert os.path.exists(recipe.image.path) is True
        assert len(os.listdir(os.path.split(recipe.image.path)[0])) == 1

    @pytest.mark.parametrize("value", ["afadfnjk", "", 1, 2.242424, False])
    def test_upload_image_bad_request(self, create_user_and_recipe, value):
        """Test uploading an invalid image"""
        user, client, recipe = create_user_and_recipe
        recipe = create_sample_recipe(user=user)
        url = reverse("recipe:recipe-upload-image", args=[recipe.id])
        res = client.post(url, {"image": value}, format="multipart")

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_image_from_recipe(self, create_user_and_recipe):
        """Test uploading an image to recipe"""
        user, client, recipe = create_user_and_recipe
        url = reverse("recipe:recipe-upload-image", args=[recipe.id])
        add_image_to_the_recipe(client, url, "JPEG")
        recipe.refresh_from_db()
        path = recipe.image.path
        delete_url = reverse("recipe:recipe-delete-image", args=[recipe.id])
        res = client.delete(delete_url)
        assert res.status_code == status.HTTP_204_NO_CONTENT
        recipe.refresh_from_db()
        assert len(os.listdir(os.path.split(path)[0])) == 0


