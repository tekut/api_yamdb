# Generated by Django 3.2 on 2023-08-23 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titles',
            name='year',
            field=models.IntegerField(verbose_name='Год выпуска'),
        ),
    ]
