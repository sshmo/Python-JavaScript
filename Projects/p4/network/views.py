import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow


class PostForm(forms.Form):
    """ Post Form """

    post = forms.CharField(label="post",
                           widget=forms.Textarea(
                               attrs={'placeholder': ' Write a new post',
                                      'rows': 1,
                                      'cols': 45,
                                      'style': 'margin-bottom:0'}))


def index(request):
    """ Index route handler """

    # Make a list of all posts
    post_list = Post.objects.all().order_by('-post_time')

    # Create a paginator instance for 10 posts per page
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Make the html context
    context = {
        "post_form": PostForm(prefix='post'),
        'page_obj': page_obj,
    }

    # if the user atttemps to write a new post
    if request.method == "POST":

        # find the current user
        user = User.objects.get(pk=int(request.user.id))

        # attemp to post the request
        post(request, user, context)

    # finally load the index page
    return render(request, "network/index.html", context)


def login_view(request):
    """ Login view handler """
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


@login_required
def logout_view(request):
    """ Logout view handler """
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

    # find the profile user
    profile_user = User.objects.get(pk=int(user_id))

    # Make a list of all of the profile user posts
    post_list = Post.objects.filter(poster=profile_user).order_by('-post_time')

    # Create a paginator instance for 10 posts per page
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the profile follow data
    # if it does not exists make a new one and get that
    try:
        profile_follow_obj = Follow.objects.get(user=profile_user)
    except ObjectDoesNotExist:
        profile_follow_obj = Follow.objects.create(user=profile_user)
        profile_follow_obj = Follow.objects.get(user=profile_user)

    # find and count all following and followrs of the profile user

    profile_following = profile_follow_obj.following.all()
    profile_following_count = profile_following.count()

    profile_followers = profile_follow_obj.followers.all()
    profile_followers_count = profile_followers.count()

    # create a new html context
    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        "following_count": profile_following_count,
        "followers_count": profile_followers_count,
    }

    # if a user is logged in and is viewing the profile:
    if request.user.id:

        # find the current user
        current_user = User.objects.get(pk=int(request.user.id))

        # uodate html context for the follow button color
        context['follow_color'] = ("primary"
                                   if current_user in profile_followers
                                   else "outline-primary")
        # add current user to the context
        context['current_user'] = current_user

        # Get the current user follow data
        # if it does not exists make a new one and get that
        try:
            current_follow_obj = Follow.objects.get(user=current_user)
        except ObjectDoesNotExist:
            current_follow_obj = Follow.objects.create(user=current_user)
            current_follow_obj = Follow.objects.get(user=current_user)

    # if current user attemps to follow/unfollow the profile user:
    if 'follow' in request.POST:

        # Attemp to update the follow state of profile and current user
        follow(request,
               current_user, profile_user,
               profile_followers,
               profile_follow_obj, current_follow_obj,
               profile_followers_count, context)
    
    # finally load the profile page
    return render(request, "network/profile.html", context)


@login_required
def post(request, current_user, context):
    """ post handler """

    # a\Attemp to save the post
    if 'post' in request.POST:

        form = PostForm(request.POST, prefix='post')

        if form.is_valid():

            # save the post
            last_post = form.cleaned_data["post"]
            post_obj = Post()
            post_obj.post = last_post
            post_obj.poster = current_user
            post_obj.save()

        else:
            context["post_form"] = form


@login_required
def follow(request,
           current_user, profile_user,
           profile_followers,
           profile_follow_obj, current_follow_obj,
           profile_followers_count, context):
    """add/remove follow list handler"""

    if 'follow' in request.POST:

        # update the following and followers data for the current user and profile user
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


@login_required
def following(request):
    """ following page handler """

    # get the current user
    current_user = User.objects.get(pk=int(request.user.id))

    # Get the current user follow data
    # if it does not exists make a new one and get that
    try:
        current_follow_obj = Follow.objects.get(user=current_user)
    except ObjectDoesNotExist:
        current_follow_obj = Follow.objects.create(user=current_user)
        current_follow_obj = Follow.objects.get(user=current_user)
    
    # find all users that the current user follows
    following_obj = current_follow_obj.following.all()

    # Make a list of all posts from the users the current user follows
    post_list = Post.objects.filter(
        poster__in=following_obj).order_by('-post_time')

    # Create a paginator instance for 10 posts per page
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Make the html context
    context = {
        "post_form": PostForm(prefix='post'),
        'page_obj': page_obj,
    }

    # if the user atttemps to write a new post
    if request.method == "POST":

        # attemp to post the request
        post(request, current_user, context)

    # finally load the index page
    return render(request, "network/index.html", context)


@csrf_exempt
@login_required
def posts(request, post_id):
    """ posts API route """

    # Query for requested Post
    try:
        post_obj = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(post_obj.serialize())

    # Update whether post is liked or should be edited
    elif request.method == "PUT":

        # Get the json data
        data = json.loads(request.body)

        # Attemp to edit a post content
        if data.get("edit") is not None:
            post_obj.post = data["edit"]

        # Attemp to like/unlike a post
        if data.get("liked") is not None:

            if data["liked"]:
                post_obj.likers.add(User.objects.get(pk=int(data["user"])))

            else:
                post_obj.likers.remove(User.objects.get(pk=int(data["user"])))

        post_obj.save()
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)
