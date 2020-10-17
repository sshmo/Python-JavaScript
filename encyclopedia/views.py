import random
from django.shortcuts import render

from . import util


def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):

    content = util.get_entry(title)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title" : title if content else "Error",
    })

def search(request): 

    title = request.GET['q']
    content = util.get_entry(title)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title" : title,
    })

def random_page(request): 

    title = random.choice(util.list_entries())
    content = util.get_entry(title)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title" : title,
    })