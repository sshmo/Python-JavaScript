from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("random/", views.random_page, name="random"),
    path("new/", views.new, name="new"),
    path("error/", views.error, name="error"),
    path("edit/<str:title>", views.edit, name="edit"),
]
