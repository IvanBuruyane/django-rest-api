from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""

    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for the recipe image"""

    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ("image",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe object"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = serializers.ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "minutes_to_cook",
            "price",
            "link",
            "ingredients",
            "tags",
            "image",
        )
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe object with tag and ingredient details"""

    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
