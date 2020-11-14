"""
This module contains the route handlers and forms.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listings, Bids


class CreateForm(forms.Form):
    """Create Form"""

    title = forms.CharField(label="Title",
                            widget=forms.TextInput(attrs={'placeholder': 'Title'}))

    description = forms.CharField(label="description",
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))

    current_bid = forms.DecimalField(max_digits=6, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'placeholder': 'Starting bid ($)'}))

    image = forms.URLField(required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Image url'}))

    categury = forms.CharField(label="Categury", required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Categury'}))


class BidForm(forms.Form):
    """Bid Form"""

    bid = forms.DecimalField(max_digits=6, decimal_places=2,
                             widget=forms.NumberInput(attrs={'placeholder': 'Place your bid ($)'}))


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

    listing_obj, context = l_context(request, listing_id)

    if not context:
        message = f'The "{listing_id}" page was not in the database.'
        return render(request, "auctions/error.html", {
            "message": message,
        })

    watchers = listing_obj.watchers.all()
    user, user_context = u_context(request, watchers, context)

    if not user_context:
        return render(request, "auctions/listing.html", context)

    if request.method == "POST":

        wacth(request, user, watchers, listing_obj, context)

        message = place_bid(request, listing_obj, user, context)

        if message == "Invalid bid":
            return render(request, "auctions/error.html", {
                "message": message,
            })

    return render(request, "auctions/listing.html", context)


def l_context(request, listing_id):
    """listing id context maker"""

    listing_obj = Listings.objects.get(pk=int(listing_id))

    if listing_obj:
        context = {
            "title": listing_obj.title,
            "description": listing_obj.description,
            "current_bid": listing_obj.current_bid,
            "image": listing_obj.image,
            "categury": listing_obj.categury,
            "form": BidForm(prefix='bid'),
            "id": listing_id,
        }

        return listing_obj, context

    return None, None


def u_context(request, watchers, context):
    """listing user context maker"""

    if request.user.id:

        user = User.objects.get(pk=int(request.user.id))

        if user in watchers:
            value = "remove"
            color = "danger"
        else:
            value = "add"
            color = "success"

        context["value"] = value
        context["color"] = color

        return user, context

    return None, None


@login_required
def wacth(request, user,  watchers, listing_obj, context):
    """add/remove watch list handler"""

    if 'watch' in request.POST:

        if user in watchers:
            listing_obj.watchers.remove(user)
            value = "add"
            color = "success"
        else:
            listing_obj.watchers.add(user)
            value = "remove"
            color = "danger"

        context["value"] = value
        context["color"] = color


@login_required
def place_bid(request, listing_obj, user, context):
    """add new bid handler"""

    if 'bid' in request.POST:

        form = BidForm(request.POST, prefix='bid')

        if form.is_valid():

            current_bid = form.cleaned_data["bid"]

            last_bid = Bids.objects.filter(listing=listing_obj).last()

            if (current_bid > listing_obj.current_bid)\
                    or ((current_bid == listing_obj.starting_bid) and (last_bid is None)):

                bids = Bids()
                bids.bidder = user
                bids.listing = listing_obj
                bids.bid = current_bid
                bids.save()

                listing_obj.current_bid = current_bid
                listing_obj.save()

                context["current_bid"] = current_bid

            else:
                return "Invalid bid"

        else:
            context["form"] = form
    return None


@login_required
def categuries(request):
    """Categuries route handler"""

    return render(request, "auctions/categuries.html")


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

        form = CreateForm(request.POST)

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
            "form": CreateForm()
        })


def error_handler(request, message):
    """Error route handler"""

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })
