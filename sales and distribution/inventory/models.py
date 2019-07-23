from django.db import models


class Add_item(models.Model):
    item_code = models.CharField(max_length = 100)
    item_name = models.CharField(max_length = 100)
    item_description = models.TextField()
    unit = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    size = models.CharField(max_length = 100)
    opening_stock = models.DecimalField(max_digits = 8, decimal_places = 2)

    def __str__(self):
        return self.item_code
