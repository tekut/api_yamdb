import csv

from django.conf import settings
from django.core.management import BaseCommand

from titles.models import Categories, Genres, Titles, GenresTitles

TABLES = {
    # Categories: 'category.csv',
    # Genres: 'genre.csv',
    # Titles: 'titles.csv',
    GenresTitles: 'genre_title.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)                
                model.objects.bulk_create(
                    model(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))