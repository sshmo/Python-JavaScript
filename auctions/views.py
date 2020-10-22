from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listings


class CreateForm(forms.Form):
    """Create Form"""

    title = forms.CharField(label="Title")
    description = forms.CharField(widget=forms.Textarea, label="description")
    starting_bid = forms.DecimalField(max_digits=6, decimal_places=2)
    image = forms.URLField(required=False)
    categury = forms.CharField(label="Categury", required=False)


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
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
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
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


@login_required
def categuries(request):
    return render(request, "auctions/categuries.html")


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html")


@login_required
def create_listings(request):

    if request.method == "POST":

        form = CreateForm(request.POST)

        if form.is_valid():

            user = User.objects.get(pk=int(request.user.id))
            listings = Listings()

            listings.user = user
            listings.title = form.cleaned_data["title"]
            listings.description = form.cleaned_data["description"]
            listings.starting_bid = form.cleaned_data["starting_bid"]
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

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })