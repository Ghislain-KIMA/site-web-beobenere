from django.shortcuts import render, redirect
from company.models import Company
from .forms import ContactForm


def contact_page(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contact:success")
    else:
        form = ContactForm()

    return render(request, "contact/page.html", {
        "form": form,
        "company": Company.objects.first(),
    })


def contact_success(request):
    return render(request, "contact/success.html")