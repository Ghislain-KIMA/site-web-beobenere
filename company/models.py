from django.db import models



# class Company(models.Model):
#     name = models.CharField(max_length=150, null=False)
#     slogan = models.CharField(max_length=255)
#     description = models.TextField()
#     sector = models.CharField(max_length=100)
#     logo_url = models.CharField(max_length=255)
#     email = models.CharField(max_length=150)
#     phone = models.CharField(max_length=30)
#     address = models.TextField()
#     created_at = models.DateTimeField()

#     def __str__(self) -> str:
#         return self.name



class Company(models.Model):
    id = models.SmallAutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=150, null=False)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=150, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=30, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
