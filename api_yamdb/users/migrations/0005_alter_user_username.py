# Generated by Django 3.2 on 2023-08-24 11:29

from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230824_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.UsernameValidator()], verbose_name='Имя пользователя'),
        ),
    ]
