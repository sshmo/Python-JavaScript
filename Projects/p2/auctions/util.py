"""
This module contains util functions and forms.
"""
from django import forms

from .models import Bids, Comments, Listings, User


class CreateForm(forms.Form):
    """Create Form"""

    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"placeholder": "Title"}))

    description = forms.CharField(label="description", widget=forms.TextInput(attrs={"placeholder": "Description"}))

    current_bid = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"placeholder": "Starting bid ($)"})
    )

    image = forms.URLField(required=False, widget=forms.TextInput(attrs={"placeholder": "Image url"}))

    categury = forms.CharField(
        label="Categury", required=False, widget=forms.TextInput(attrs={"placeholder": "Categury"})
    )


class BidForm(forms.Form):
    """Bid Form"""

    bid = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"placeholder": "Place your bid ($)"})
    )


class CommentForm(forms.Form):
    """Comment Form"""

    comment = forms.CharField(label="comment", widget=forms.Textarea(attrs={"placeholder": "Add your comment"}))


def place_bid(request, listing_obj, user, context):
    """add new bid handler"""

    if "bid" in request.POST:

        form = BidForm(request.POST, prefix="bid")

        if form.is_valid():

            current_bid = form.cleaned_data["bid"]

            last_bid = Bids.objects.filter(listing=listing_obj).last()

            if (current_bid > listing_obj.current_bid) or (
                (current_bid == listing_obj.starting_bid) and (last_bid is None)
            ):

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
            context["bid_form"] = form
    return None


def wacth(request, user, watchers, listing_obj, context):
    """add/remove watch list handler"""

    if "watch" in request.POST:

        if user in watchers:
            listing_obj.watchers.remove(user)
            color = "outline-dark"
        else:
            listing_obj.watchers.add(user)
            color = "dark"

        context["color"] = color


def close(request, user, listing_obj, context):
    """closes the bid if owner wants"""

    if "close" in request.POST:

        if user == listing_obj.creator:
            listing_obj.status = False
            listing_obj.save()
            context["status"] = "Closed"
        else:
            return "Invalid request"

    return None


def comment(request, listing_obj, user, context):
    """comment handler"""

    if "comment" in request.POST:

        form = CommentForm(request.POST, prefix="comment")

        if form.is_valid():

            last_comment = form.cleaned_data["comment"]
            comment_obj = Comments()
            comment_obj.comment = last_comment
            comment_obj.commenter = user
            comment_obj.listing = listing_obj
            comment_obj.save()

        else:
            context["comment_form"] = form


def listing_context(request, listing_id):
    """listing context maker"""

    listing_obj = Listings.objects.get(pk=int(listing_id))
    last_bid = Bids.objects.filter(listing=listing_obj).last()
    bidder = last_bid.bidder if last_bid is not None else None
    comments = Comments.objects.filter(listing=listing_obj)

    if listing_obj:
        context = {
            "title": listing_obj.title,
            "description": listing_obj.description,
            "current_bid": listing_obj.current_bid,
            "image": listing_obj.image,
            "categury": listing_obj.categury,
            "bid_form": BidForm(prefix="bid"),
            "comment_form": CommentForm(prefix="comment"),
            "id": listing_id,
            "status": "Active" if listing_obj.status else "Closed",
            "creator": listing_obj.creator,
            "bidder": bidder,
            "comments": comments,
        }

        return listing_obj, context

    return None, None


def user_context(request, watchers, context):
    """listing user context maker"""

    if request.user.id:

        user = User.objects.get(pk=int(request.user.id))

        if user in watchers:
            color = "dark"
        else:
            color = "outline-dark"

        context["color"] = color

        return user, context

    return None, None
