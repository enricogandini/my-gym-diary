# Generated by Django 4.2.7 on 2023-11-19 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='workout',
            constraint=models.UniqueConstraint(fields=('date',), name='unique_date'),
        ),
    ]
