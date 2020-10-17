from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("entry/<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("random/", views.random_page, name="random")
]
