import simplejson as json

from django.views.generic import DetailView
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from cellcounter.accounts.models import UserProfile, PasswordResetKey
from cellcounter.accounts.forms import UserCreateForm, UserNameReminderForm, RequestPasswordResetForm, SetPasswordForm, PasswordChangeForm, EmailChangeForm
from cellcounter.mixins import JSONResponseMixin
from django.contrib.auth.models import User

import os, sys
from django.conf import settings
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

#from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

import random
import string
from datetime import datetime

class KeyboardLayoutView(JSONResponseMixin, DetailView):
    """
    Return a JSON description of the users keyboard mapping
    """
    model = UserProfile

    def get_object(self):
        # Find the UserProfile from the request session
        if self.request.user.is_authenticated():
            return self.model.objects.get(user=self.request.user)
        else:
            return json.load(open(os.path.join(settings.PROJECT_DIR,
                'accounts/keyboard.json'), 'r'))

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return self.object.keyboard or {}
        else:
            #print >> sys.stderr, "test"
            return json.load(open(os.path.join(settings.PROJECT_DIR,
                'accounts/keyboard.json'), 'r'))

    # TODO Enable csrf checking
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(KeyboardLayoutView, self).dispatch(*args, **kwargs)

    # TODO Should do validation of mapping?
    def post(self, request, *args, **kwargs):
        """
        Takes a JSON body and sets that as the users keyboard mapping
        """
        if self.request.user.is_authenticated():
            # Get the user profile object
            self.object = self.get_object()
            # Get keyboard definition
            self.object.keyboard = json.loads(request.raw_post_data)
            # Save the change
            self.object.save()
            # Return with accepted but no content
            return HttpResponse("", status=204)
        else:
            # Return forbidden
            return HttpResponse("", status=403)

def register(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            saved_form = form.save()
            user = authenticate(username = form.cleaned_data["username"], 
                                password = form.cleaned_data["password1"])
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreateForm()
    return render_to_response('accounts/register.html',
                              {'form': form,},
                              context_instance=RequestContext(request))

def forgotten_username(request):
    if request.method == "POST":
        form = UserNameReminderForm(request.POST)
        if form.is_valid():
            for user in User.objects.filter(email = form.cleaned_data["email"]):
                context = Context({"username": user.username})
                text_content = get_template("accounts/username_reminder.text").render(context)
                html_content = get_template("accounts/username_reminder.html").render(context)
                msg = EmailMultiAlternatives('CellCountr username reminder', text_content, settings.AUTO_EMAIL_ADDRESS, [form.cleaned_data["email"]])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            return HttpResponseRedirect(reverse("username_reminder_sent"))
    else:
        form = UserNameReminderForm()
    return render_to_response('accounts/forgotten_username.html',
                              {'form': form,},
                              context_instance=RequestContext(request))

def forgotten_password(request):
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username = form.cleaned_data["username"])
            charset = string.ascii_uppercase + string.digits
            key = ''.join(random.choice(charset) for x in range(30))
            PasswordResetKey(user = user, key = key, expiry = datetime.now() + settings.PASSWORD_RESET_KEY_DURATION).save()
            context = Context({"username": user.username, "key": key, "SERVER_NAME": settings.SERVER_NAME})
            text_content = get_template("accounts/password_reset_email.text").render(context)
            html_content = get_template("accounts/password_reset_email.html").render(context)
            msg = EmailMultiAlternatives('CellCountr password reset token', text_content, settings.AUTO_EMAIL_ADDRESS, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return HttpResponseRedirect(reverse("username_reminder_sent"))
    else:
        form = RequestPasswordResetForm()
    return render_to_response('accounts/forgotten_password.html',
                              {'form': form,},
                              context_instance=RequestContext(request))

def password_reset(request, key):
    prk = get_object_or_404(PasswordResetKey, key=key)
    if prk.expiry < datetime.now():
        raise Http404()
    if request.method == "POST":
        form = SetPasswordForm(prk.user, request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username = prk.user.username, 
                                password = form.cleaned_data["new_password1"])
            login(request, user)
            prk.delete()
            return HttpResponseRedirect(reverse("password_reset"))
    else:
        form = SetPasswordForm(prk.user)
    return render_to_response('accounts/reset_password.html',
                              {'form': form,},
                              context_instance=RequestContext(request))    

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("password_reset"))
    else:
        form = PasswordChangeForm(request.user)
    return render_to_response('accounts/change_password.html',
                              {'form': form,},
                              context_instance=RequestContext(request)) 

@login_required
def change_email(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("email_reset"))
    else:
        form = EmailChangeForm(instance = request.user)
    return render_to_response('accounts/change_email.html',
                              {'form': form,},
                              context_instance=RequestContext(request)) 
