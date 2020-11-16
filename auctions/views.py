"""
This module contains the route handlers.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings
from . import util


def index(request):
    """Index route handler"""

    items = Listings.objects.all()

    return render(request, "auctions/index.html", {
        'items': items
    })


def login_view(request):
    """Login route handler"""

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """logout route handler"""

    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    """register route handler"""

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):
    """Listing route handler"""

    listing_obj, context = util.listing_context(request, listing_id)

    if not context:
        message = f'The "{listing_id}" page was not in the database.'
        return render(request, "auctions/error.html", {
            "message": message,
        })

    watchers = listing_obj.watchers.all()
    user, user_context = util.user_context(request, watchers, context)

    if not user_context:
        return render(request, "auctions/listing.html", context)

    if request.method == "POST":

        util.wacth(request, user, watchers, listing_obj, context)

        util.comment(request, listing_obj, user, context)

        message = util.place_bid(request, listing_obj, user, context)

        if message is not None:
            return render(request, "auctions/error.html", {
                "message": message,
            })

        message = util.close(request, user, listing_obj, context)

        if message is not None:
            return render(request, "auctions/error.html", {
                "message": message,
            })

    return render(request, "auctions/listing.html", context)


@login_required
def categuries(request):
    """Categuries route handler"""

    categury_names = Listings.objects.all().values_list(
        'categury', flat=True).distinct()

    return render(request, "auctions/categuries.html", {
        "categuries": categury_names
    })


@login_required
def categury(request, name):
    """categury route handler"""

    items = Listings.objects.filter(categury=name)

    return render(request, "auctions/index.html", {
        "items": items
    })


@login_required
def watchlist(request):
    """Watchlist route handler"""

    user = User.objects.get(pk=int(request.user.id))
    items = user.listings_set.all()

    return render(request, "auctions/watchlist.html", {
        "items": items
    })


@login_required
def create_listings(request):
    """Creat route handler"""

    if request.method == "POST":

        form = util.CreateForm(request.POST)

        if form.is_valid():

            user = User.objects.get(pk=int(request.user.id))
            listings = Listings()

            listings.creator = user
            listings.title = form.cleaned_data["title"]
            listings.description = form.cleaned_data["description"]
            listings.starting_bid = form.cleaned_data["current_bid"]
            listings.current_bid = form.cleaned_data["current_bid"]
            listings.image = form.cleaned_data["image"]
            listings.categury = form.cleaned_data["categury"]

            listings.save()

            # util.save_entry(title, content)
            return HttpResponseRedirect(reverse("auctions:index"))

        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": util.CreateForm()
        })


def error_handler(request, message):
    """Error route handler"""

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })
