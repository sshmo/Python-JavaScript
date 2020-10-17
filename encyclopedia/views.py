import random
from django.shortcuts import render

from . import util


def index(request):

    random_title = random.choice(util.list_entries())

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "random_title":random_title
    })


def entry(request, title):

    random_title = random.choice(util.list_entries())

    content = util.get_entry(title)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title" : title if content else "Error",
        "random_title":random_title
    })