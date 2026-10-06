from django.db import DatabaseError
from django.shortcuts import render

from company.models import Company


def homepage(request):
    try:
        company = Company.objects.first()
    except DatabaseError:
        company = None

    return render(request, "homepage/index.html", {"company": company})

def about(request):
    return render(request, "homepage/about.html")