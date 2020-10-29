"""
This module contains admin models.
"""

from django.contrib import admin

# Register your models here.

from auctions.models import Listings, User, Bids

admin.site.register(Listings)
admin.site.register(User)
admin.site.register(Bids)
