import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_create_user_with_email_successful():
    """Test creating a new user with an email is successful"""
    email = "test@londonappdev.com"
    password = "Password123"
    user = get_user_model().objects.create_user(email=email, password=password)
    assert user.email == email
    assert user.check_password(password) is True


@pytest.mark.django_db
def test_new_user_email_normalized():
    email = "test@LonDOnaPPDev.cOm"
    user = get_user_model().objects.create_user(email=email, password="123")
    assert user.email == email.lower()
