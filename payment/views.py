from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
import urllib3
import certifi
import json

from superuser.models import Order
from superuser.views import generate_invoice, send_new_task_email, email_to_customer
from worker.models import Worker


http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

def checkout(request):
    if request.method == 'GET':
        order_id = request.GET['order_id']
        product_cost = Order.objects.get(pk=order_id).product_cost
        quantity = Order.objects.get(pk=order_id).review_quantity
        amount = "{:.2f}".format((product_cost + settings.REVIEW_COST) * quantity)
    return render(request, "payment/checkout.html", {'amount': amount, 'order_id': order_id})

def confirm(request):
    if request.method == 'POST':
        try:
            current_domain = request.META['HTTP_HOST']
            customer_ip = request.POST.get('customer_ip', False)
            holder_name = request.POST['holder_name']
            card_number = request.POST['card_number']
            card_number = "".join(card_number.split())
            expire_month = request.POST['expire_month']
            expire_year = request.POST['expire_year']
            cvv = request.POST['cvv']
            order_id = request.POST['order_id']
            amount = request.POST['amount']
            amount = int(float(amount) * 100)
            values = {
                "merchantRefNum": "merchant 03.24.17_3",
                "amount": amount,
                "settleWithAuth": False,
                "dupCheck": False,
                "card": {
                    "cardNum": card_number,
                    "cardExpiry": {
                        "month": expire_month,
                        "year": expire_year
                    },
                    "cvv": cvv
                },
                "profile": {
                "firstName": "Joe",
                "lastName": "Smith",
                "email": "Joe.Smith@canada.com"
                },
                "billingDetails": {
                "street": "100 Queen Street West",
                "city": "Toronto",
                "state": "ON",
                "country": "CA",
                "zip": "M5H 2N2"
                },
                "customerIp": customer_ip,
                "description": "Order Purchase"
            }
            request_body = json.dumps(values)
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic {}'.format(settings.PAYSAFE_BASE_64_APIKEY)
            }
            request = http.request(
                'POST',
                'https://api.test.paysafe.com/cardpayments/v1/accounts/{}/auths'.format(settings.PAYSAFE_ID), 
                body=request_body, 
                headers=headers
            )
            print(json.loads(request.data.decode('utf-8')))
            response = json.loads(request.data.decode('utf-8'))
            if response['status'] == 'COMPLETED':
                order = Order.objects.get(pk=order_id)
                order.paid = True
                order.save()
                email_to_customer(order.id, current_domain, order.buyer_email, paid=True)
                send_new_task_email(current_domain, order.id)
                return HttpResponse("Success")
            else:
                return HttpResponse("Please input the valid data")
        except Exception as e:
            print(e)
            return HttpResponse(str(e))
    else:
        return HttpResponse("Get method is not allowed")