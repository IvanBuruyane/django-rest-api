import os

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from core.models import Tag, Ingredient, Recipe

from recipe import serializers
from rest_framework.response import Response


class BaseRecipeAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for user owned recipe attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset = self.queryset.filter(user=self.request.user).order_by("-id")
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        tags_list = tags.split(",") if self.request.query_params.get("tags") else []
        ingredients_list = ingredients.split(",") if self.request.query_params.get("ingredients") else []
        final_queryset = (
            queryset.filter(
                Q(tags__id__in=tags_list) | Q(ingredients__id__in=ingredients_list)
            )
            if (tags or ingredients)
            else queryset
        )

        return final_queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        return serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        if request_serializer.is_valid():
            instance = self.perform_create(request_serializer)
            response_serializer = serializers.RecipeDetailSerializer(instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                request_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        request_serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if request_serializer.is_valid(raise_exception=True):
            self.perform_update(request_serializer)
            response_serializer = serializers.RecipeDetailSerializer(instance)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                request_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response_serializer = serializers.RecipeDetailSerializer(instance)
        return Response(response_serializer.data)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        try:
            path = recipe.image.path
        except:
            path = None
        if path:
            os.remove(path)
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            response_serializer = serializers.RecipeDetailSerializer(recipe)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["DELETE"], detail=True, url_path="delete-image")
    def delete_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        path = recipe.image.path
        recipe.image = None
        os.remove(path)
        recipe.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
