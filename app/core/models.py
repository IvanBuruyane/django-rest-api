from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    User,
)
from django.core.validators import validate_email
from typing import Optional, Any


class UserManager(BaseUserManager):
    def create_user(
        self, email: Optional[str], password: Optional[str] = None, **extra_fields
    ) -> Any:
        normalized_email = self.normalize_email(email)
        validate_email(normalized_email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: Optional[str], password: Optional[str] = None
    ) -> Any:
        superuser = self.create_user(email=email, password=password)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
