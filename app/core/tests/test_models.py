def test_create_user_with_email_successful(django_user_model):
    """Test creating a new user with an email is successful"""
    email = "test@londonappdev.com"
    password = "Password123"
    user = django_user_model.objects.create(email=email, password=password)

    assert user.email == email
    assert user.check_password(password) is True
