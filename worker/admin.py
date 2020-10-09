from django.contrib import admin
from .models import Worker, Task, Payout_Request

admin.site.register(Worker)
admin.site.register(Task)
admin.site.register(Payout_Request)
