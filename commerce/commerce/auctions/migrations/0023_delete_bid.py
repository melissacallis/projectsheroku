# Generated by Django 4.2.5 on 2023-09-09 03:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0022_listing_current_price"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Bid",
        ),
    ]
