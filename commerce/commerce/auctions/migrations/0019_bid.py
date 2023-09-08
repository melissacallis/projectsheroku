# Generated by Django 4.2.3 on 2023-09-05 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0018_remove_listing_comment_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bid",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bid_amount", models.DecimalField(decimal_places=2, max_digits=6)),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to="auctions.listing",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]