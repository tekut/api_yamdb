from decimal import Decimal

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from users.models import User
from reviews.models import Review, Comment, Titles, Genres, Categories


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
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = 'name', 'year', 'rating', 'description', 'genre', 'category',
        model = Titles

    def get_rating(self, obj):
        title = Titles.objects.get(id=obj.id)
        reviews = title.reviews.all()
        rating = 0
        if reviews:
            for review in reviews:
                rating += review.score
            average_value = Decimal(rating / len(reviews))
            return average_value.quantize(Decimal("1.00"))
        return None


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


class NoRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if author.reviews.filter(title=title_id):
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
