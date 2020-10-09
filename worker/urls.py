from django.urls import path
from django.conf.urls import url

from . import views as worker_views

urlpatterns = [
    path('', worker_views.home, name='home'),
    path('dashboard/', worker_views.dashboard, name='dashboard'),
    path('purchase_instructions/', worker_views.purchase_instructions, name='purchase_instructions'),
    path('review_instructions/', worker_views.review_instructions, name='review_instructions'),
    path('tasks/', worker_views.claimed_tasks),
    path('payout/', worker_views.payouts),
    path('profile/', worker_views.profile, name='profile'),
    path('help/', worker_views.help),
    url(r'^claim_task/$', worker_views.claim, name='claim'),
    url(r'^payment_update/$', worker_views.payment_update, name='payment_update'),
    url(r'^upload_product_screenshot/$', worker_views.upload_product_screenshot, name='upload_product_screenshot'),
    url(r'^upload_review_screenshot/$', worker_views.upload_review_screenshot, name='upload_review_screenshot'), 
    url(r'^request_payout/$', worker_views.request_payout, name='request_payout'),
]