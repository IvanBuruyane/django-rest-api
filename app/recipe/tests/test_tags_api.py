import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from helpers.test_helpers import create_and_authenticate_user, random_string

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


@pytest.mark.django_db
class TestsPrivateTagsApi:
    """Test the authorized user tags API"""

    def test_login_required(self, client):
        """Test that login required for retrieving tags"""
        res = client.get(TAGS_URL)

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

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        user, client = create_and_authenticate_user()
        payload = {"name": "Simple"}
        client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=user, name=payload["name"]).exists()
        assert exists is True

    @pytest.mark.parametrize("name", ["", None, random_string(n=256)])
    def test_create_tag_invalid(self, name):
        """Test creating a new tag with invalid payload"""
        user, client = create_and_authenticate_user()
        payload = {"name": name}
        if not name:
            payload.pop("name")
        res = client.post(TAGS_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST
