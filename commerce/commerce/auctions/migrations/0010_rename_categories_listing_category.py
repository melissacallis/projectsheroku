# Generated by Django 4.1.7 on 2023-04-17 03:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_listing_categories_alter_listing_image_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='categories',
            new_name='category',
        ),
    ]