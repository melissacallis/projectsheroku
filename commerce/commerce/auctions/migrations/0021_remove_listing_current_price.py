# Generated by Django 4.2.5 on 2023-09-09 03:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0020_listing_current_price"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="listing",
            name="current_price",
        ),
    ]