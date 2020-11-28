from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Post(models.Model):
    """Posts model"""

    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")
    post = models.TextField()
    post_time = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)