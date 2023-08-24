from titles.models import Titles, Genres, Categories
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from users.models import User


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


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Нельзя создать логин с именем me'
            )
        return data

    class Meta:
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
