from django.urls import path
from django.conf.urls import url

from . import views as superuser_views

urlpatterns = [
    path('', superuser_views.home),
    path('purchase/', superuser_views.purchase_screenshots),
    path('review/', superuser_views.review_screenshots),
    path('payout_requests/', superuser_views.payout_requests),
    path('order_create/', superuser_views.create_order),
    path('update_order/', superuser_views.update_order),
    path('screenshot_popup_modal/', superuser_views.screenshot_popup_modal),
    path('approve_screenshot/', superuser_views.approve_screenshot), 
    path('reject_screenshot/', superuser_views.reject_screenshot), 
    path('mark_as_paid/', superuser_views.mark_as_paid),
]