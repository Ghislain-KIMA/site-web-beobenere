from django.shortcuts import render, redirect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import DevisForm



@sensitive_post_parameters()
def devis_create(request):
    if request.method == "POST":
        form = DevisForm(request.POST)
        # Piège rempli : c'est un robot. On affiche la page de remerciement
        # comme si tout s'était bien passé, mais on n'enregistre rien.
        if form["website"].value():
            return redirect("devis:success")
        if form.is_valid():
            form.save()
            return redirect("devis:success")
    else:
        form = DevisForm()

    return render(request, "devis/form.html", {"form": form})


def devis_success(request):
    return render(request, "devis/success.html")
