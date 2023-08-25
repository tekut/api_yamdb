from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


class Categories(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.TextField(max_length=256)
    year = models.IntegerField('Год выпуска')
    description = models.TextField(null=True)
    genre = models.ManyToManyField(Genres,
                                   related_name='titles',
                                   )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва к произведению."""
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Titles, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        'Оценка',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    """Модель комментария к отзыву."""
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    def __str__(self):
        return self.text[:50]
