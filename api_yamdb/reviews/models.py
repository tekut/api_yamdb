from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User
from api.validators import chek_year


class Category(models.Model):
    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Индентификатор', max_length=50, unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Индентификатор', max_length=50, unique=True)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField('Наименование', max_length=256)
    year = models.IntegerField('Год выпуска', validators=(chek_year,))
    description = models.TextField('Описание', null=True)
    genre = models.ManyToManyField(
        Genres,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'заголовок'
        verbose_name_plural = 'Заголовки'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва к произведению."""
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        'Оценка',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique review',
            )
        ]

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
