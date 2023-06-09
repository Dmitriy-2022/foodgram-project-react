# Generated by Django 3.2 on 2023-05-13 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodgramuser',
            name='is_subscribed',
            field=models.BooleanField(default=False, verbose_name='Подписка'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='username',
            field=models.CharField(blank=True, max_length=150, unique=True, verbose_name='Логин'),
        ),
    ]
