from django.shortcuts import render, redirect
from .forms import ContactForm
from django.views.decorators.debug import sensitive_post_parameters



@sensitive_post_parameters()
def contact_page(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        # Piège rempli : c'est un robot. On affiche la page de remerciement
        # comme si tout s'était bien passé, mais on n'enregistre rien.
        if form["website"].value():
            return redirect("contact:success")
        if form.is_valid():
            form.save()
            return redirect("contact:success")
    else:
        form = ContactForm()

    return render(request, "contact/page.html", {"form": form})


def contact_success(request):
    return render(request, "contact/success.html")
