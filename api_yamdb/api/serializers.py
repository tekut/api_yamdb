from titles.models import Titles, Genres, Categories
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = 'name', 'slug',


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genres
        fields = 'name', 'slug',


class TitlesSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(slug_field='name', read_only=True)
    genre = SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        fields = 'name', 'year', 'description', 'genre', 'category',
        model = Titles
