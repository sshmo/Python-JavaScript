"""
This module contains urls.
"""

from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categuries", views.categuries, name="categuries"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create_listings, name="create"),
    path("error/", views.error_handler, name="error"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("categury/<str:name>", views.categury, name="categury"),
]
