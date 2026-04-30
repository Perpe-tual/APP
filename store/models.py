from django.db import models

# A Model is like a table in a spreadsheet.
# Each Product has a name, description, price, image URL, age range, and category.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('clothing', 'Clothing'),
        ('shoes', 'Shoes'),
        ('hats', 'Hats & Beanies'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=200)         # product name
    description = models.TextField()                 # long description
    price = models.DecimalField(max_digits=6, decimal_places=2)  # e.g. 12.99
    image_url = models.URLField(blank=True)          # link to a product image
    age_range = models.CharField(max_length=50)      # e.g. "0–3 months"
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False) # show on homepage?

    def __str__(self):
        return self.name  # shows product name in admin panel 