from django.db import models
from django.contrib.auth.models import User
import datetime

from superuser.models import Order


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    used_ips = models.CharField(max_length=255)
    bitcoin_address = models.CharField(max_length=40, null=True, blank=True)
    order_notification = models.BooleanField(null=True, blank=True)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    claimed_date = models.DateTimeField()
    product_screenshot = models.ImageField(upload_to='product_screenshots/', default='product_screenshots/non.jpg') 
    purchased_date = models.DateTimeField(null=True, blank=True)
    review_screenshot = models.ImageField(upload_to='review_screenshots/', default='review_screenshots/non.jpg') 
    status = models.CharField(max_length=20)
    
    def save(self, *args, **kwargs):
        self.claimed_date = self.claimed_date.replace(tzinfo=None)
        super(Task, self).save(*args, **kwargs)


class Payout_Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.OneToOneField(Task, null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(null=True)
    payout_method = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=50)
    date_submitted = models.DateField(default=datetime.date.today)
    date_paid = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)
