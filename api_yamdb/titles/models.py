from django.db import models


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
