# Generated by Django 4.2.1 on 2023-05-15 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0016_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='comment',
            field=models.TextField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]
