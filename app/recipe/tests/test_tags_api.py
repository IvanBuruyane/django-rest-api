import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from helpers.test_helpers import create_and_authenticate_user, random_string

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


@pytest.mark.django_db(reset_sequences=True)
class TestsPrivateTagsApi:
    """Test the authorized user tags API"""

    @pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
    def test_login_required(self, client, method):
        """Test that login is required to access this endpoint"""
        if method == "get":
            res = client.get(TAGS_URL)
        elif method == "post":
            res = client.post(TAGS_URL)
        elif method == "put":
            res = client.put(reverse("recipe:tag-detail", kwargs={"pk": "1"}))
        elif method == "delete":
            res = client.delete(reverse("recipe:tag-detail", kwargs={"pk": "1"}))

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        Tag.objects.create(user=user, name="Dessert")

        res = client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user, client = create_and_authenticate_user()
        user2 = get_user_model().objects.create_user(
            "other@londonappdev.com", "testpass"
        )
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=user, name="Comfort Food")

        res = client.get(TAGS_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["name"] == tag.name

    def test_retrieve_one_tag(self):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        Tag.objects.create(user=user, name="Dessert")
        url = reverse("recipe:tag-detail", kwargs={"pk": "2"})

        res = client.get(url)

        tag = Tag.objects.get(pk=2)
        serializer = TagSerializer(tag)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_retrieve_non_existent_tag(self, value):
        """Test retrieving tags"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        url = reverse("recipe:tag-detail", kwargs={"pk": value})

        res = client.get(url)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        user, client = create_and_authenticate_user()
        payload = {"name": "Simple"}
        client.post(TAGS_URL, payload, format="json")

        exists = Tag.objects.filter(user=user, name=payload["name"]).exists()
        assert exists is True

    @pytest.mark.parametrize("name", ["", None, random_string(n=256)])
    def test_create_tag_invalid(self, name):
        """Test creating a new tag with invalid payload"""
        user, client = create_and_authenticate_user()
        payload = {"name": name}
        if not name:
            payload.pop("name")
        res = client.post(TAGS_URL, payload, format="json")

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_tag_successful(self):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        url = reverse("recipe:tag-detail", kwargs={"pk": 1})
        res = client.put(url, {"name": "updated_vegan"})
        serializer = TagSerializer(Tag.objects.get(id=1))

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_update_non_existent_tag(self, value):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        url = reverse("recipe:tag-detail", kwargs={"pk": value})
        res = client.put(url, {"name": "updated_vegan"})
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "payload",
        [{"name": ""}, {}, {"name": random_string(n=256)}, {"incorrect_key": "value"}],
    )
    def test_update_tag_incorrect_payload(self, payload):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        url = reverse("recipe:tag-detail", kwargs={"pk": 1})
        res = client.put(url, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_tag_successful(self):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        Tag.objects.create(user=user, name="Vegan")
        url = reverse("recipe:tag-detail", kwargs={"pk": 1})
        res = client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert client.get(url).status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("value", [2, "efef"])
    def test_delete_non_existent_tag(self, value):
        """Test updating a new tag"""
        user, client = create_and_authenticate_user()
        url = reverse("recipe:tag-detail", kwargs={"pk": value})
        res = client.delete(url)

        assert res.status_code == status.HTTP_404_NOT_FOUND
