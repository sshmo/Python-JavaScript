from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """ User model """


class Post(models.Model):
    """ Post model """

    poster = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="poster")
    post = models.TextField()
    post_time = models.DateTimeField(default=timezone.now)
    likers = models.ManyToManyField(User, related_name="post_likers")

    def serialize(self):
        """ Converts the post content to json format """
        return {
            "id": self.id,
            "poster": self.poster.username,
            "likers": [liker.id for liker in self.likers.all()],
            "post": self.post,
            "timestamp": self.post_time.strftime("%b %-d %Y, %-I:%M %p"),
        }

    def likes(self):
        """ Total likes counter """
        return self.likers.all().count()


class Follow(models.Model):
    """ Following model """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follow_user")
    following = models.ManyToManyField(User, related_name="follow_following")
    followers = models.ManyToManyField(User, related_name="follow_followers")
