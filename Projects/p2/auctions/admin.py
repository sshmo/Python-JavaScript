"""
This module contains admin models.
"""

from auctions.models import Bids, Comments, Listings, User
from django.contrib import admin

# Register your models here.


admin.site.register(Listings)
admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Comments)
