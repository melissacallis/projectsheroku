# Generated by Django 4.1.7 on 2023-04-12 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_created_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='created_by',
        ),
    ]
