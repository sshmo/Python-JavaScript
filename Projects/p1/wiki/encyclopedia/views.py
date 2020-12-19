import random

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import markdown2
from . import util


class NewForm(forms.Form):
    """ New form """
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")


class EditForm(forms.Form):
    """ Edit form """
    content = forms.CharField(widget=forms.Textarea, label="Content")


def index(request):
    """
        Index route handler

        Inputs: request
        Output: Index page
    """

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):
    """
        Entry route handler

        Inputs:
            request
            title of the page

        Output:
            Entry page
            If not exists then raise error
    """

    # get page content using util function
    content = util.get_entry(title)

    if content:

        # convert the content to markdown format
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
    """
        Search route handler

        Inputs:
            request

        Output:
            Found exact page
            If not exists then list of similar pages
            If not found raise error
    """

    # get the page title using "q" key
    title = request.GET['q']

    # get page content using util function
    content = util.get_entry(title)

    # if exact match was found:
    if content:

        # convert the content to markdown format
        content = markdown2.markdown(text=content)
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title": title,
        })

    # if exact match was not found try to find similar pages
    entries = util.list_entries()

    # find similar pages
    results = [entry for entry in entries if title.lower() in entry.lower()]

    # if similar pages was found:
    if results:
        return render(request, "encyclopedia/results.html", {
            "entries": results,
        })

    # if nothing was found:
    else:
        message = f'There is no page containing "{title}" in the database.'
        return render(request, "encyclopedia/error.html", {
            "message": message,
        })


def random_page(request):
    """
        Random page handler

        Inputs:
            request

        Output:
            random page
    """

    # find random page using choice function
    title = random.choice(util.list_entries())

    # get page content using util function
    content = util.get_entry(title)

    # convert the content to markdown format
    content = markdown2.markdown(text=content)

    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title": title,
    })


def new(request):
    """
        New page handler

        Inputs:
            request

        Output:
            Makes a new page
            If title was already taken raise error
    """

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
    """
        Edit page handler

        Inputs:
            request
            title of the target page

        Output:
            Edited page
    """

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
    """
        Error handler

        Inputs:
            request
            error message

        Output:
            Error page with the message
    """

    return render(request, "encyclopedia/error.html", {
        "message": message,
    })
