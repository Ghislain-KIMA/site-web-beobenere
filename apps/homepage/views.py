from django.shortcuts import render

from company.models import Company



def homepage(request):
    # récupère la première entreprise en base de données.
    # Comme il n'y a qu'une seule entreprise, c'est celle-ci que l'on veut afficher.
    company = Company.objects.first() 
    return render(request, "homepage/index.html", {"company": company})
