# Generated by Django 4.2.7 on 2023-11-19 13:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0002_alter_exercise_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='code',
            field=models.CharField(max_length=5, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z]*$', 'Only letters are allowed.')]),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='name',
            field=models.CharField(max_length=25, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z ]*$', 'Only letters and spaces are allowed.')]),
        ),
    ]
