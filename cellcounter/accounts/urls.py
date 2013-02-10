from django.conf.urls import patterns, url 
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from cellcounter.accounts.views import KeyboardLayoutView, register, forgotten_username, forgotten_password, password_reset, change_email, change_password, delete_account

urlpatterns = patterns('',
    url(r'^keyboard/$', KeyboardLayoutView.as_view()),
    url(r'^register/$', register),
    url(r'^forgotten_username/$', forgotten_username, name="forgotten_username"),
    url(r'^forgotten_password/$', forgotten_password, name="forgotten_password"),
    url(r'^password_reset/(.+)$', password_reset, name="password_reset"),
    url(r'^reminder_sent/$', direct_to_template, {'template': 'accounts/reminder_sent.html'}, name="username_reminder_sent"),
    url(r'^password_reset/$', direct_to_template, {'template': 'accounts/password_reset.html'}, name="password_reset"),
    url(r'^manage/$', direct_to_template, {'template': 'accounts/manage.html'}, name="manage_my_account"),
    url(r'^change_email/$', change_email, name="change_email"),
    url(r'^email_reset/$', direct_to_template, {'template': 'accounts/email_reset.html'}, name="email_reset"),
    url(r'^change_password/$', change_password, name="change_password"),
    url(r'^delete_account/$', delete_account, name="delete_account"),
    url(r'^account_deleted/$', direct_to_template, {'template': 'accounts/account_deleted.html'}, name="account_deleted"),
)
