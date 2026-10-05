from django.shortcuts import render, redirect
from company.models import Company
from .forms import ContactForm
from django.views.decorators.debug import sensitive_post_parameters



@sensitive_post_parameters()
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
