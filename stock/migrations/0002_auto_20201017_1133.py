# Generated by Django 3.1.1 on 2020-10-17 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=models.CharField(max_length=100)),
        ),
    ]
