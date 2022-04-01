import pytest
from django.contrib.auth import get_user_model
from django.db import connections
from helpers.db_helpers import run_sql, wait_for_db


@pytest.fixture(scope="function")
def setup_admin(client):
    admin_user = get_user_model().objects.create_superuser(
        email="admin@londonappdev.com", password="123"
    )
    client.force_login(admin_user)
    user = get_user_model().objects.create_user(
        email="test_user@londonappdev.com", password="123", name="Test User"
    )
    return {"admin_user": admin_user, "user": user}


# @pytest.fixture(scope="session", autouse=True)
# def django_db_setup():
#     wait_for_db()
#
#     run_sql("DROP DATABASE IF EXISTS test_postgres_db")
#     run_sql("CREATE DATABASE test_postgres_db")
#
#     yield
#
#     for connection in connections.all():
#         connection.close()
#
#     run_sql("DROP DATABASE test_postgres_db")
