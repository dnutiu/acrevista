"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.shortcuts import render


# TODO: PROFILE, HISTORY, REVIEW PAGES
# Homepage of the Journal
def homepage(request):
    return render(request, "journal/index.html", {'section': 'journal'})

