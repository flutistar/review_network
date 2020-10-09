from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^login_superuser/$', views.lgoin_superuser_view, name='login_superuser'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^logout_superuser/$', views.logout_superuser_view),
    url('signup_success/', views.signup_success, name='signup_success'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='register/password_change_done.html'), name='password_change_done'),
    path('pssword_change/', auth_views.PasswordChangeView.as_view(template_name='register/password_change.html'), name='password_change'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='register/password_reset_done.html'), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(template_name='register/password_reset_form.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='register/password_reset.html'), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='register/password_reset_complete.html'), name='password_reset_complete'),

]
