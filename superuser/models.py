from django.db import models
import datetime

 
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateField(default=datetime.date.today)
    platform = models.CharField(max_length=50)
    platform_country = models.CharField(default=".com", max_length=10)
    product_id = models.CharField(max_length=50)
    buyer_email = models.CharField(max_length=30)
    buyer_company_name = models.CharField(max_length=30)
    review_quantity = models.IntegerField()
    earning = models.FloatField(default=10)
    days_to_complete = models.IntegerField(default=10)
    product_cost = models.FloatField(default=0.00)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % (self.creation_date, self.product_cost)
