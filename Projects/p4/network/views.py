from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Post

class PostForm(forms.Form):
    """Post Form"""

    post = forms.CharField(label="post",
                              widget=forms.Textarea(attrs={'placeholder': 'Write a new post', 'rows': 1, 'cols': 45,}))

def index(request):

    context = general_context(request)

    if request.method == "POST":

        user = User.objects.get(pk=int(request.user.id))

        print(user)

        post(request, user, context)

    return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


def post(request, user, context):
    """post handler"""

    if 'post' in request.POST:

        form = PostForm(request.POST, prefix='post')

        if form.is_valid():

            last_post = form.cleaned_data["post"]
            post_obj = Post()
            post_obj.post = last_post
            post_obj.poster = user
            post_obj.save()

        else:
            context["post_form"] = form


def general_context(request):
    """general context handler"""

    posts = Post.objects.all().order_by('-post_time')

    context = {
    "post_form": PostForm(prefix='post'),
    "posts": posts,
    }

    return context