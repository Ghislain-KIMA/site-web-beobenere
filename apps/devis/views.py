from django.shortcuts import render, redirect
from .forms import DevisForm


def devis_create(request):
    if request.method == "POST":
        form = DevisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("devis:success")
    else:
        form = DevisForm()

    return render(request, "devis/form.html", {"form": form})


def devis_success(request):
    return render(request, "devis/success.html")