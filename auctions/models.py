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
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.URLField(max_length=200)  # Not using ImageFeild to avoid Pillow dependency.
    categury = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __str__(self):
        return f"{self.title} ({self.categury})"


class Bids(models.Model):
    """Bids model"""


class Comments(models.Model):
    """Comments model"""
