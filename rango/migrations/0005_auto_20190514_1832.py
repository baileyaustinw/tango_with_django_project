# Generated by Django 2.1 on 2019-05-14 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0004_auto_20181210_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='first_visit',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='last_visit',
            field=models.DateField(null=True),
        ),
    ]
