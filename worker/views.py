import asyncio
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages
from django.template.loader import render_to_string

from datetime import datetime, timedelta
from django.conf import settings

from superuser.models import Order
from worker.models import Task, Worker, Payout_Request
from .forms import ImageUploadForm

from threading import Thread
import time

company_name = settings.COMPANY_NAME

# View of worker/home(dashboard)
@login_required
def home(request):
    return redirect('/dashboard/')
 

# View of worker/home(dashboard)
@login_required
def dashboard(request):
    balance = getBalance(request.user.id)
    user = User.objects.get(pk=request.user.id)
    notification = Worker.objects.get(user=user).order_notification
    rows = Order.objects.filter(paid=True)
    user = User.objects.get(pk=request.user.id)
    orders = []
    for row in rows:
        if (not Task.objects.filter(order=row, user=user)) \
            or (Task.objects.filter(order=row, user=user, status=settings.TASK_STATUS['cancelled']) \
                and len(Task.objects.filter(order=row, user=user)) < 3):
            # Calculate remaining quantity of the reviews
            remaining = len(Task.objects.filter(order=row)) - len(
                Task.objects.filter(order=row, status=settings.TASK_STATUS['cancelled']))
            if remaining < row.review_quantity:
                temp = {}
                done = str(remaining) + ' / ' + str(row.review_quantity)
                temp['id'] = row.id
                temp['product_cost'] = row.product_cost
                temp['earning'] = row.earning
                temp['done'] = done
                temp['platform'] = row.platform
                temp['platform_country'] = row.platform_country
                orders.append(temp)
    context = {
        'company_name': company_name,
        'page': 'Available Tasks',
        'orders': orders,
        'balance': balance,
        'notification': notification
    }
    return render(request, 'worker/worker_home.html', context)


# View of worker/claimed_task
@login_required
def claimed_tasks(request):
    tasks = []
    balance = getBalance(request.user.id)
    user = User.objects.get(pk=request.user.id)
    rows = Task.objects.filter(user=user)
    # Get data from Order and Task model
    for row in rows:
        order = Order.objects.get(pk=row.order_id)
        temp = {
            'id': row.id,
            'price': order.product_cost,
            'earning': order.earning,
            'platform': order.platform + order.platform_country,
            'claimed_date': row.claimed_date.date(),
            'end_date': row.claimed_date.date() + timedelta(days=order.days_to_complete),
            'status': row.status
        }
        tasks.append(temp)
    context = {
        'company_name': company_name,
        'page': 'Claimed Tasks',
        'tasks': tasks,
        'balance': balance
    }
    return render(request, 'worker/claimed_tasks.html', context)


# View of worker/payouts
@login_required
def payouts(request):
    balance = getBalance(request.user.id)
    task_status = settings.TASK_STATUS['approved']
    user = User.objects.get(pk=request.user.id)
    payment_methods = settings.PAYMENT_METHODS
    tasks = Task.objects.filter(user=user, status=task_status)
    rows = Payout_Request.objects.filter(user=user)
    payout_histories = []
    for row in rows:
        tmp = {}
        tmp['id'] = row.id
        tmp['date_submitted'] = row.date_submitted
        tmp['date_paid'] = row.date_paid
        order = Order.objects.get(pk=row.order)
        tmp['amount'] = order.earning + order.product_cost
        tmp['status'] = row.status
        payout_histories.append(tmp)
    approved_tasks = []
    for task in tasks:
        order = Order.objects.get(pk=task.order_id)
        temp = {
            'id': task.id,
            'amount': order.earning + order.product_cost
        }
        approved_tasks.append(temp)
    context = {
        'company_name': company_name,
        'page': 'Payouts',
        'payment_methods': payment_methods,
        'approved_tasks': approved_tasks,
        'payout_histories': payout_histories,
        'balance': balance
    }
    return render(request, 'worker/payouts.html', context)


@login_required
def request_payout(request):
    if request.method == 'POST':
        task_status = settings.TASK_STATUS['approved']
        user = User.objects.get(pk=request.user.id)
        payment_methods = request.POST['payment']
        wallet_address = Worker.objects.get(user=user).bitcoin_address
        if not wallet_address:
            messages.error(request, 'You have to add the bitcoin address!')
            return redirect('/profile/')
        tasks = Task.objects.filter(user=user, status=task_status)
        for task in tasks:
            order = Order.objects.get(pk=task.order_id)
            amount = order.earning + order.product_cost
            payout_request = Payout_Request(
                user=user,
                task=task,
                order=order.id,
                payout_method=payment_methods,
                wallet_address=wallet_address,
                status=settings.PAYMENT_STATUS['pending']
            )
            payout_request.save()
            task.status = settings.TASK_STATUS['pending']
            task.save()
        messages.success(request, 'You submitted payout request successfully!')
    return redirect('/payout/')


# View of worker/profile
@login_required
def profile(request):
    balance = getBalance(request.user.id)
    user = Worker.objects.get(user=request.user.id)
    notification = user.order_notification
    bitcoin_address = user.bitcoin_address
    context = {
        'company_name': company_name,
        'page': 'Profile',
        'notification': notification,
        'bitcoin_address': bitcoin_address,
        'balance': balance,
    }
    return render(request, 'worker/profile.html', context)


# View of worker/help
@login_required
def help(request):
    balance = getBalance(request.user.id)
    context = {
        'company_name': company_name,
        'page': 'Help',
        'username': request.user.username,
        'balance': balance
    }
    return render(request, 'worker/help.html', context)


# View of worker/claim task
@login_required
def claim(request):
    balance = getBalance(request.user.id)
    order = Order.objects.get(pk=request.GET['order_id'])
    user = User.objects.get(pk=request.user.id)
    task = Task(
        user=user,
        status=settings.TASK_STATUS['claimed'],
        order=order,
        claimed_date=datetime.now()
    )
    task.save()
    ASIN = order.product_id
    # Generate product link
    product_link = "https://www." + order.platform + order.platform_country + '/dp/' + ASIN
    context = {
        'company_name': company_name,
        'page': 'worker_instruction',
        'product_link': product_link,
        'balance': balance,
        'task': task.id
    }
    return render(request, 'worker/purchase_instructions.html', context)


# View of payment update. Called from worker/payment/submit payment method
@login_required
def payment_update(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == "POST":
        worker = Worker.objects.get(user=user)
        worker.bitcoin_address = request.POST['bitcoin_address']
        if request.POST['order_notification'] == 'true' and worker.order_notification == False:
            worker.order_notification = True
            """Send an email that changed the email notifiaction"""
        elif request.POST['order_notification'] == 'false' and worker.order_notification == True:
            worker.order_notification = False
        worker.save()
        return HttpResponse('Success')
    return HttpResponse('Failed')

# View of upload product screenshot. Called from worker/purchase instuction/ upload screenshot
@login_required
def upload_product_screenshot(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            task = Task.objects.get(pk=form.cleaned_data['task'])
            task.status = settings.TASK_STATUS['purchased']
            task.product_screenshot = form.cleaned_data['screenshot']
            task.purchased_date = datetime.now()
            task.save()
            messages.success(request, 'Upload screenshot successful')
            return redirect('/tasks/')
        else:
            return HttpResponse(form.cleaned_data['task'])
    return HttpResponse('allowed only via POST')


# View of upload product screenshot. Called from worker/purchase instuction/ upload screenshot
@login_required
def upload_review_screenshot(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            task = Task.objects.get(pk=form.cleaned_data['task'])
            task.status = settings.TASK_STATUS['review']
            task.review_screenshot = form.cleaned_data['screenshot']
            task.save()
            messages.success(request, 'Upload screenshot successful')
            return redirect('/tasks/')
        else:
            return HttpResponse(form.cleaned_data['task'])
    return HttpResponse('allowed only via POST')


# Called from worker/claimed_task/submit
@login_required
def purchase_instructions(request):
    balance = getBalance(request.user.id)
    task_id = request.GET['task_id']
    task = Task.objects.get(pk=task_id)
    order = Order.objects.get(pk=task.order_id)
    ASIN = order.product_id
    product_link = "https://www." + order.platform + order.platform_country + '/dp/' + ASIN
    context = {
        'company_name': company_name,
        'page': 'worker_instruction',
        'product_link': product_link,
        'balance': balance,
        'task': task.id
    }
    return render(request, 'worker/purchase_instructions.html', context)


@login_required
def review_instructions(request):
    balance = getBalance(request.user.id)
    task_id = request.GET['task_id']
    context = {
        'company_name': company_name,
        'task': task_id,
        'balance': balance
    }
    return render(request, 'worker/review_instructions.html', context)


def getBalance(user_id):
    user = User.objects.get(pk=user_id)
    approved_tasks = Task.objects.filter(user=user, status=settings.TASK_STATUS['approved'])
    sum = 0
    for approved_task in approved_tasks:
        order = Order.objects.get(pk=approved_task.order_id)
        sum += order.earning
        sum += order.product_cost
    return sum
