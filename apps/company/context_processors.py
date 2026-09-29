from .models import Company


def company(request):
    return {"site_company": Company.objects.first()}
