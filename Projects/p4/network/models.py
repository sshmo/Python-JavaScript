from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """User model"""


class Post(models.Model):
    """Post model"""

    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")
    post = models.TextField()
    post_time = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)


class Follow(models.Model):
    """Following model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_user")
    following = models.ManyToManyField(User, related_name="follow_following")
    followers = models.ManyToManyField(User, related_name="follow_followers")