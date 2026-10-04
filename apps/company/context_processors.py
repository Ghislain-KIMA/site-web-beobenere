from django.db import DatabaseError

from .models import Company


def company(request):
    try:
        site_company = Company.objects.first()
    except DatabaseError:
        site_company = None

    return {"site_company": site_company}