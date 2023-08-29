# Generated by Django 3.1.1 on 2020-11-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stock', '0003_auto_20201020_2142'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40)),
                ('url', models.CharField(max_length=40)),
                ('products', models.ManyToManyField(to='stock.Product')),
            ],
        ),
    ]