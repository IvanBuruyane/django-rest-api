from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    email = serializers.EmailField(
        trim_whitespace=True,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(min_length=5, write_only=True, required=True)
    name = serializers.CharField(max_length=255, min_length=3)

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
