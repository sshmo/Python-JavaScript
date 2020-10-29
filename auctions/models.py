"""
This module contains database models.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Users model"""


class Listings(models.Model):
    """Listings model"""

    title = models.CharField(max_length=64)
    description = models.TextField()
    current_bid = models.DecimalField(max_digits=6, decimal_places=2, default=0.01)
    image = models.URLField(max_length=200, default=None, blank=True, null=True)
    categury = models.CharField(max_length=64, default=None, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listing")
    watchers = models.ManyToManyField(User, default=None, blank=True)

    def __str__(self):
        return f"{self.title} ({self.categury})"


class Bids(models.Model):
    """Bids model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bid")
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    """Comments model"""
