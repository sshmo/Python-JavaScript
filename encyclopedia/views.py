import random
import markdown2
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import util


class NewForm(forms.Form):
    """New form"""
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")


class EditForm(forms.Form):
    """Edit form"""
    content = forms.CharField(widget=forms.Textarea, label="Content")


def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):

    content = util.get_entry(title)
    
    if content:
        content = markdown2.markdown(text=content)
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title": title,
        })
    else:
        message = f'The "{title}" page was not in the database.'
        return render(request, "encyclopedia/error.html", {
            "message": message,
        })


def search(request):

    title = request.GET['q']
    content = util.get_entry(title)
    
    if content:
        content = markdown2.markdown(text=content)
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title": title,
        })
    
    entries = util.list_entries()
    results = [entry for entry in entries if title.lower() in entry.lower()]
    
    if results:
        return render(request, "encyclopedia/results.html", {
            "entries": results,
        })
 
    else:
        message = f'There is no page containing "{title}" in the database.'
        return render(request, "encyclopedia/error.html", {
            "message": message,
        })


def random_page(request):

    title = random.choice(util.list_entries())
    content = util.get_entry(title)
    content = markdown2.markdown(text=content)

    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title": title,
    })


def new(request):

    if request.method == "POST":

        form = NewForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data["title"]

            if title in util.list_entries():

                message = f'There is already a page with the title:"{title}"\
                in the database.'

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


def edit(request, title):

    if request.method == "POST":

        form = EditForm(request.POST)

        if form.is_valid():

            content = form.cleaned_data["content"]
            util.save_entry(title, content)

            content = markdown2.markdown(text=content)
            return render(request, "encyclopedia/entry.html", {
                "content": content,
                "title": title,
            })

        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title,
            })
    else:

        content = util.get_entry(title)
        form = EditForm(initial={'content': content})

        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title,
        })


def error_handler(request, message):

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })
