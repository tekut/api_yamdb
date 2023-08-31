from pprint import pprint

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genres, Review, Title, GenreTitle
from users.models import User
from users.validators import UsernameValidator


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id', )


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genres
        exclude = ('id', )


class TitlesSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer()
    genre = GenresSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'rating', 'year',
                  'description', 'genre', 'category')
        model = Title


    def get_rating(self, obj):
        ratings_avg = Title.objects.annotate(rating=Avg('reviews__score'))
        for title in ratings_avg:
            if title.id == obj.id:
                return title.rating


class TitlesPostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genres.objects.all(),
        many=True
    )

    class Meta:
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')
        model = Title

    def to_representation(self, value):
        return TitlesSerializer(value, context=self.context).data


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150,
                                     required=True,
                                     validators=[UsernameValidator()]
                                     )

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве `username` запрещено."
            )
        return data

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
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


class NoRoleSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            author = request.user
            title_id = self.context.get('view').kwargs.get('title_id')
            if author.reviews.filter(title=title_id).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв к этому произведению.'
                )
        return data

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )
