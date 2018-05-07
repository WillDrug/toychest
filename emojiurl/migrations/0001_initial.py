# Generated by Django 2.0 on 2018-05-07 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('emoji', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('link', models.URLField()),
                ('keep_alive', models.IntegerField()),
            ],
        ),
    ]
