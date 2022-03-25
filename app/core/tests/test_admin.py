import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_users_listed(setup_admin, client):
    """Test that users are listed on the user page"""
    url = reverse("admin:core_user_changelist")
    user = setup_admin["user"]
    r = client.get(url)
    print(user.name, user.email)

    assert r.status_code == 200
    assert user.name in str(r.content) and user.email in str(r.content)
