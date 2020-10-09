import time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from worker.models import Task
from .tasks import send_cancellation_email_task

def checkTaskStatus():
    tasks = Task.objects.filter(status = settings.TASK_STATUS['claimed'])
    emails = []
    for task in tasks:
        td = datetime.now() - task.claimed_date.replace(tzinfo=None)
        ts = td.total_seconds()
        if int(ts/60) > 60:
            task.status = settings.TASK_STATUS['cancelled']
            task.save()
            send_cancellation_email_task.delay(User.objects.get(pk=task.user_id).email, task.id)

def send_cancellation_email(email, task_id):
    email_subject = 'Your task has been cancelled.'
    email_content = render_to_string('emails/cancellation.html', {
        'task_id': task_id,
    })
    Message = EmailMessage(email_subject, email_content , to=[email])
    Message.send()

def remindPurchasedProof():
    tasks = Task.objects.filter(status = settings.TASK_STATUS['purchased'])
    emails = []
    for task in tasks:
        if task.purchased_date and datetime.now() - task.purchased_date.replace(tzinfo=None) > timedelta(days=5):
            emails.append(User.objects.get(pk=task.user_id).email)
    email_subject = "It's time to write your review"
    to_email = User.objects.get(pk=task.user_id).email
    email_content = render_to_string('emails/reminder.html')
    email = EmailMessage(email_subject, email_content , to=emails)
    email.send()
