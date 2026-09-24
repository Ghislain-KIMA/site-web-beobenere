from django.db import models



class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        db_table = "category"
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    brief_description = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="services",
    )

    class Meta:
        db_table = "service"
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name