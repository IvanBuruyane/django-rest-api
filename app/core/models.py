import uuid
import os
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    User,
)
from django.core.validators import validate_email
from typing import Optional, Any
from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate filepath for the new recipe image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/recipe/", filename)


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


class Tag(models.Model):
    """Tag to be used for a recipe"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    minutes_to_cook = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField(max_length=255, blank=True)
    ingredients = models.ManyToManyField("Ingredient")
    tags = models.ManyToManyField("Tag")
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
