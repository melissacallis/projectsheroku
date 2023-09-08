# Generated by Django 4.1.7 on 2023-04-16 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_remove_listing_html_listing_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='category',
        ),
        migrations.AddField(
            model_name='listing',
            name='categories',
            field=models.CharField(choices=[('Electronics', 'Category 1'), ('Readings', 'Category 2'), ('Clothing', 'Category 3')], default=1, max_length=20),
        ),
    ]
