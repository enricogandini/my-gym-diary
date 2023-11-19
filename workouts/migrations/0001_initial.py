# Generated by Django 4.2.7 on 2023-11-19 12:05

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5, unique=True)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='exercise',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('code'), name='unique_code'),
        ),
        migrations.AddConstraint(
            model_name='exercise',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_name'),
        ),
        migrations.AddConstraint(
            model_name='exercise',
            constraint=models.UniqueConstraint(fields=('code', 'name'), name='unique_exercise'),
        ),
    ]