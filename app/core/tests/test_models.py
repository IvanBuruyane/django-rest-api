import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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
    """Test the email for a new user is normalized"""
    email = "test@LonDOnaPPDev.cOm"
    user = get_user_model().objects.create_user(email=email, password="123")
    assert user.email == email.lower()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_email",
    [
        None,
        "example.com",
        "A@b@c@domain.com",
        "a”b(c)d,e:f;gi[j\k]l@domain.com",
        "abc”test”email@domain.com",
        "abc is”not\valid@domain.com",
        "abc\ is\”not\valid@domain.com",
        ".test@domain.com",
        "test@domain..com",
    ],
)
def test_new_user_invalid_email(invalid_email):
    """Test creation user with empty email raises error"""
    with pytest.raises(ValidationError):
        get_user_model().objects.create_user(email=invalid_email, password="123")
