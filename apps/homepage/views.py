from django.shortcuts import render



def homepage(request):
    return render(request, "homepage/index.html")


def about(request):
    return render(request, "homepage/about.html")


def legal(request):
    return render(request, "homepage/legal.html")