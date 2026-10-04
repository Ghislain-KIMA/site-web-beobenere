from itertools import zip_longest

from django.shortcuts import render
from .models import Category, Service



def service_list(request):
    categories = Category.objects.all().order_by("id")
    selected_slug = request.GET.get("categorie")

    if selected_slug:
        # Un filtre est actif : liste simple de cette seule catégorie
        services = Service.objects.filter(
            category__slug=selected_slug, is_active=True
        ).select_related("category").order_by("id")
    else:
        # Pas de filtre : entrelacement round-robin entre toutes les catégories
        per_category = [
            list(Service.objects.filter(category=cat, is_active=True).order_by("id"))
            for cat in categories
        ]
        services = []
        for group in zip_longest(*per_category):
            for service in group:
                if service is not None:
                    services.append(service)

    return render(request, "service/list.html", {
        "services": services,
        "categories": categories,
        "selected_slug": selected_slug,
    })
