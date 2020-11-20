"""
This module contains database models.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Users model"""


class Listings(models.Model):
    """Listings model"""

    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2, default=0.01)
    current_bid = models.DecimalField(max_digits=6, decimal_places=2, default=0.01)
    image = models.URLField(max_length=200, default=None, blank=True, null=True)
    categury = models.CharField(max_length=64, default=None, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    creation_time = models.DateTimeField(default=timezone.now)
    watchers = models.ManyToManyField(User, default=None, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.categury})"


class Bids(models.Model):
    """Bids model"""

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bid")
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    bid_time = models.DateTimeField(default=timezone.now)


class Comments(models.Model):
    """Comments model"""

    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    comment = models.TextField()
    comments_time = models.DateTimeField(default=timezone.now)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comment")
