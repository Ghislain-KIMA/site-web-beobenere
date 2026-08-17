from django.db import models



class Company(models.Model):
    name = models.CharField(max_length=150, null=False)
    slogan = models.CharField(max_length=255)
    description = 

