from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from .models import User, Post, Follow


class PostForm(forms.Form):
    """Post Form"""

    post = forms.CharField(label="post",
                           widget=forms.Textarea(attrs={'placeholder': ' Write a new post', 'rows': 1, 'cols': 45, 'style': 'margin-bottom:0'}))


def index(request):

    post_list = Post.objects.all().order_by('-post_time')
    paginator = Paginator(post_list, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "post_form": PostForm(prefix='post'),
        'page_obj': page_obj,
    }

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
    """register route handler"""

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


def profile(request, user_id):
    """user profile handler"""

    profile_user = User.objects.get(pk=int(user_id))

    post_list = Post.objects.filter(poster=profile_user).order_by('-post_time')
    paginator = Paginator(post_list, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    try:
        profile_follow_obj = Follow.objects.get(user=profile_user)
    except ObjectDoesNotExist:
        profile_follow_obj = Follow.objects.create(user=profile_user)
        profile_follow_obj = Follow.objects.get(user=profile_user)

    profile_following = profile_follow_obj.following.all()
    profile_following_count = profile_following.count()

    profile_followers = profile_follow_obj.followers.all()
    profile_followers_count = profile_followers.count()

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        "following_count": profile_following_count,
        "followers_count": profile_followers_count,
    }

    if request.user.id:
        current_user = User.objects.get(pk=int(request.user.id))

        context['follow_color'] = "primary" if current_user in profile_followers else "outline-primary"
        context['current_user'] = current_user

        try:
            current_follow_obj = Follow.objects.get(user=current_user)
        except ObjectDoesNotExist:
            current_follow_obj = Follow.objects.create(user=current_user)
            current_follow_obj = Follow.objects.get(user=current_user)

    if 'follow' in request.POST:

        follow(request, current_user, profile_user, profile_followers,
               profile_follow_obj, current_follow_obj, profile_followers_count, context)

    return render(request, "network/profile.html", context)


def post(request, current_user, context):
    """post handler"""

    if 'post' in request.POST:

        form = PostForm(request.POST, prefix='post')

        if form.is_valid():

            last_post = form.cleaned_data["post"]
            post_obj = Post()
            post_obj.post = last_post
            post_obj.poster = current_user
            post_obj.save()

        else:
            context["post_form"] = form


def follow(request, current_user, profile_user, profile_followers, profile_follow_obj, current_follow_obj, profile_followers_count, context):
    """add/remove follow list handler"""

    if 'follow' in request.POST:

        if current_user in profile_followers:
            profile_follow_obj.followers.remove(current_user)
            current_follow_obj.following.remove(profile_user)
            color = "outline-primary"
            profile_followers_count -= 1
        else:
            profile_follow_obj.followers.add(current_user)
            current_follow_obj.following.add(profile_user)
            profile_followers_count += 1
            color = "primary"

        profile_follow_obj.save()
        current_follow_obj.save()
        context["follow_color"] = color
        context["followers_count"] = profile_followers_count


def following(request):

    current_user = User.objects.get(pk=int(request.user.id))

    try:
        current_follow_obj = Follow.objects.get(user=current_user)
    except ObjectDoesNotExist:
        current_follow_obj = Follow.objects.create(user=current_user)
        current_follow_obj = Follow.objects.get(user=current_user)
    
    following = current_follow_obj.following.all()

    post_list = Post.objects.filter(poster__in=following).order_by('-post_time')
    paginator = Paginator(post_list, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        "post_form": PostForm(prefix='post'),
        'page_obj': page_obj,
    }

    if request.method == "POST":

        user = User.objects.get(pk=int(request.user.id))

        print(user)

        post(request, user, context)

    return render(request, "network/index.html", context)
