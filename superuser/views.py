from datetime import date, timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q

from django.conf import settings

from worker.models import Task, Payout_Request, Worker

from .models import Order
from .utils import render_to_pdf

# current_site = Site.objects.get_current()
company_name = settings.COMPANY_NAME

@login_required(login_url='/account/login_superuser/')
def home(request):
    context = {
        'company_name': company_name,
        'page': 'create'
    }
    return render(request, 'superuser/create_order.html', context)
 

@login_required(login_url='/account/login_superuser/')
def purchase_screenshots(request):
    rows = Task.objects.filter(Q(status=settings.TASK_STATUS['purchased']) | Q(status=settings.TASK_STATUS['review']))
    tasks = []
    if rows:
        for row in rows:
            temp = {
                'id': row.id,
                'screenshot': row.product_screenshot.url
            }
            tasks.append(temp)
    context = {
        'company_name': company_name,
        'page': 'purchase',
        'tasks': tasks
    }
    return render(request, 'superuser/purchase_screenshots.html', context)


@login_required(login_url='/account/login_superuser/')
def review_screenshots(request):
    rows = Task.objects.filter(status=settings.TASK_STATUS['review'])
    tasks = []
    if rows:
        for row in rows:
            temp = {
                'id': row.id,
                'screenshot': row.review_screenshot.url
            }
            tasks.append(temp)
    
    context = {
        'company_name': company_name,
        'page': 'review',
        'tasks': tasks
    }
    return render(request, 'superuser/review_screenshots.html', context)


@login_required(login_url='/account/login_superuser/')
def payout_requests(request):
    payouts = Payout_Request.objects.all()
    results = []
    for payout in payouts:
        tmp = {}
        tmp['id'] = payout.id
        tmp['user'] = payout.user
        tmp['task'] = payout.task
        order = Order.objects.get(pk=payout.order)
        tmp['amount'] = order.earning + order.product_cost
        tmp['payout_method'] = payout.payout_method
        tmp['wallet_address'] = payout.wallet_address
        tmp['date_submitted'] = payout.date_submitted
        tmp['date_paid'] = payout.date_paid
        tmp['status'] = payout.status
        results.append(tmp)
    context = {
        'company_name': company_name,
        'page': 'payout',
        'payouts': results
    }
    return render(request, 'superuser/payout_requests.html', context)

@login_required(login_url='/account/login_superuser/')
def mark_as_paid(request):
    if request.method == 'GET':
        payout_id = request.GET['payout_id']
        payout_request = Payout_Request.objects.get(pk=payout_id)
        task = Task.objects.get(pk=payout_request.task_id)
        payout_request.status = settings.PAYMENT_STATUS['completed']
        payout_request.date_paid = date.today()
        task.status = settings.TASK_STATUS['completed']
        payout_request.save()
        task.save()
        messages.success(request, "Mark as paid successfully!")
        return redirect('/manage/payout_requests/')


def generate_invoice(order_id, current_domain, paid=False):
    order = Order.objects.get(pk=order_id)
    #Invocie context
    context = {
        'invoice_id': order.id,
        'current_domain': current_domain,
        'logo_src': 'http://' + current_domain + '/static/images/logo.png',
        'paid_src': 'http://' + current_domain + '/static/images/paid.png',
        'created_date': date.today(),
        #Our company
        'site_name': settings.SITE_NAME,
        # 'contact_email' settings.DEFAULT_FROM_EMAIL,
        #Buyer company
        'buyer_email': order.buyer_email,
        'buyer_company_name': order.buyer_company_name,
        #Order detail
        'product_id': order.product_id,
        'platform': order.platform,
        'review_cost': settings.REVIEW_COST,
        'review_quantity': order.review_quantity,
        'product_cost': order.product_cost,
        'review_total': settings.REVIEW_COST * order.review_quantity,
        'product_total': order.product_cost * order.review_quantity,
        'total': (settings.REVIEW_COST + order.product_cost) * order.review_quantity,
        'days_to_complete': order.days_to_complete,
        'paid': paid,        
    }
    # template = get_template('superuser/invoice.html')
    # html = template.render(context)
    pdf = render_to_pdf('superuser/invoice.html', context)
    print('invoice is generated')
    print(pdf)
    return pdf


def create_order(request):
    current_domain = request.META['HTTP_HOST']
    if request.method == 'POST':
        try:
            order = Order(
                platform=request.POST['platform'],
                product_id=request.POST['product_id'],
                buyer_email=request.POST['buyer_email'],
                buyer_company_name=request.POST['buyer_company'],
                review_quantity=request.POST['quantity'],
                earning=request.POST['earning'],
                product_cost=request.POST['cost'],
                days_to_complete=request.POST['days_to_complete'],
            )
            order.save()
            invoice = generate_invoice(order.id, current_domain)
            
            email_subject = 'Payment Due - Invoice for Vamux Order #' + str(order.id)
            to_email = request.POST['buyer_email']
            message = render_to_string('emails/create_order.html', {
                'platform': request.POST['platform'],
                'product_id': request.POST['product_id'],
                'status': 'created',
            })
            email = EmailMessage(email_subject, message, to=[to_email])
            email.attach_file(invoice)
            email.send()
            return HttpResponse("Success.")
        except Exception as e:
            print(e)
            return HttpResponse(str(e))

def send_new_task_email(current_domain, order_id):
    print('send new task email')
    email_subject = 'New Available Tasks'
    workers = Worker.objects.filter(order_notification=True)
    to_emails = []
    for worker in workers:        
        to_emails.append(User.objects.get(pk=worker.user_id).email)
    message_html = render_to_string('emails/new_available_task.html', {
        'order_id': order_id,
        'current_domain':  current_domain,
    })
    message_text = render_to_string('emails/new_available_task_text.html', {
        'order_id': order_id,
    })
    try:
        email = EmailMultiAlternatives(email_subject, message_text, settings.DEFAULT_FROM_EMAIL, to=to_emails)
        email.attach_alternative(message_html, "text/html")
        email.send()
        print('Sent email')
    except Exception as e:
        print('Raised an error when send the new available task emails')

def email_to_customer(order_id, current_domain, customer_email, paid=False, platform='', product_id=''):
    invoice = generate_invoice(order_id, current_domain, paid=paid)  
    if paid:
        email_subject = 'Congratulations!'
        email_content = render_to_string('emails/order_is_available.html')
    else:
        email_subject = 'Payment Due - Invoice for Vamux Order #' + str(order_id)
        email_content = render_to_string('emails/create_order.html', {
            'platform': platform,
            'product_id': product_id,
            'status': 'updated',
        })
    email = EmailMessage(email_subject, email_content, to=[customer_email])
    email.attach_file(invoice)
    email.send()

def update_order(request):
    current_domain = request.META['HTTP_HOST']
    if request.method == 'POST':
        try:
            if request.POST['paid'] == 'on':
                paid = True
            else:
                paid = False
            order = Order.objects.get(pk=request.POST['id'])
            """ Check if updated. """
            if order.paid != paid and paid == True:
                email_to_customer(order.id, current_domain, order.buyer_email, paid)
                send_new_task_email(current_domain, order.id)
                return HttpResponse("Mark as paid successfully!")
            if(
                str(order.product_id) != request.POST['product_id'] or
                order.buyer_email != request.POST['buyer_email'] or
                order.buyer_company_name != request.POST['buyer_company_name'] or
                str(order.review_quantity) != request.POST['review_quantity'] or
                str(order.earning) != request.POST['earning'] or
                str(order.product_cost) != request.POST['product_cost'] or
                str(order.days_to_complete) != request.POST['days_to_complete'] or
                order.paid != paid
            ):   
                print("order is updated")
                email_to_customer(order.id, current_domain, order.buyer_email, paid, request.POST['platform'], request.POST['product_id'])
                return HttpResponse("Update successfully!")
            else:
                return HttpResponse("Nothing happened")
        except Exception as e:
            return HttpResponse(str(e))

@login_required(login_url='/account/login_superuser/')
def screenshot_popup_modal(request):
    if request.method == 'GET':
        task = Task.objects.get(pk=request.GET['task_id'])
        if request.GET['page'] == 'product':
            screenshot = task.product_screenshot.url
        elif request.GET['page'] == 'review':
            screenshot = task.review_screenshot.url
        return HttpResponse(screenshot)
    return HttpResponse('Failed')


@login_required(login_url='/account/login_superuser/')
def approve_screenshot(request):
    if request.method == 'GET':
        task = Task.objects.get(pk=request.GET['task_id'])
        task.status = settings.TASK_STATUS['approved']
        task.save()
        return HttpResponse('You approved a task succesfully.')
    return HttpResponse('Failed')


@login_required(login_url='/account/login_superuser/')
def reject_screenshot(request):
    if request.method == 'POST':
        task_id = request.POST['task_id']
        email_content = render_to_string('emails/reject.html', {
            'task_id': task_id,
            'reject_text': request.POST['reject_text'],
        })
        # email_content = request.POST['reject_text']
        task = Task.objects.get(pk=task_id)
        task.status = settings.TASK_STATUS['rejected']
        task.save()
        to_email = User.objects.get(pk=task.user_id).email
        email_subject = 'Your review screenshot has been rejected'
        email = EmailMessage(email_subject, email_content, to=[to_email])
        email.send()
        return HttpResponse('You rejected a task.')
    return HttpResponse('Failed')
