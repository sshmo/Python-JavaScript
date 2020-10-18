import random
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import util

class NewForm(forms.Form):
    """New form"""
    title = forms.CharField(label="Title")
    content = forms.CharField(widget= forms.Textarea, label="Content")

def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):

    content = util.get_entry(title)
    if content:
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title" : title,
            })
    else:
            message = f"The {title} page was not in the database."
            return render(request, "encyclopedia/error.html", {
            "message": message,
            })

def search(request): 

    title = request.GET['q']
    content = util.get_entry(title)
    
    if content:
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title" : title,
            })
    else:
            message = f"The {title} page was not found."
            return render(request, "encyclopedia/error.html", {
            "message": message,
            })

def random_page(request): 

    title = random.choice(util.list_entries())
    content = util.get_entry(title)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title" : title,
    })

def new(request): 

    if request.method == "POST":
        
        form = NewForm(request.POST)
        
        if form.is_valid():
            
            title = form.cleaned_data["title"]

            if title in util.list_entries():
                
                message = f'The is already an article with the title:"{title}" in the database.'
                return render(request, "encyclopedia/error.html", {
                "message": message,
                })
            
            else:

                content = form.cleaned_data["content"]
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:new"))
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": NewForm()
        })

def error(request, message): 

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })