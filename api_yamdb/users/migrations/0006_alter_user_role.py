# Generated by Django 3.2 on 2023-08-31 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('moderator', 'Moderator'), ('user', 'User')], default='user', max_length=20, verbose_name='Роль'),
        ),
    ]
