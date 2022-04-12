from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    email = serializers.EmailField(trim_whitespace=True, required=True)
    password = serializers.CharField(min_length=5, write_only=True, required=True)
    name = serializers.CharField(max_length=255, min_length=3, required=True)

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
