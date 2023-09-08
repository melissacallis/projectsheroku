from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid




class User(AbstractUser):
    pass

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)


class Listing(models.Model):
    CATEGORIES = (
    ('books', 'Books'),
    ('electronics', 'Electronics'),
    ('fashion', 'Fashion'),
    ('home', 'Home'),
    ('sport', 'Sport'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", default=1)
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=2000, default='')
    category = models.CharField(max_length=20, choices=CATEGORIES, default='books')
    #comment = models.TextField(max_length=500, default='')
    live = models.BooleanField(default=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    created = models.DateTimeField(default=timezone.now, blank=True)


    def save(self, *args, **kwargs):
        # Override the save method to update the current_price when a new bid is placed
        highest_bid = self.bids.order_by('-bid_amount').first()
        if highest_bid:
            self.current_price = highest_bid.bid_amount
        else:
            self.current_price = self.starting_price
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listings = models.ManyToManyField(Listing, blank=True, related_name="watchlists")

    def __str__(self):
        return self.user.username.capitalize() + "'s Watchlist"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=500)
    created = models.DateTimeField(default=timezone.now)





