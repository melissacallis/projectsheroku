# Generated by Django 4.2.5 on 2023-09-09 03:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0021_remove_listing_current_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="current_price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]