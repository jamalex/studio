import json
import os
from datetime import date
from datetime import datetime
from datetime import timedelta

from django.conf import settings as ccsettings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from rest_framework.decorators import api_view

from .json_dump import json_for_parse_from_data
from .json_dump import json_for_parse_from_serializer
from contentcuration.decorators import browser_is_supported
from contentcuration.decorators import has_accepted_policies
from contentcuration.forms import DeleteAccountForm
from contentcuration.forms import IssueReportForm
from contentcuration.forms import PolicyAcceptForm
from contentcuration.forms import StorageRequestForm
from contentcuration.forms import UsernameChangeForm
from contentcuration.serializers import UserSettingsSerializer
from contentcuration.tasks import generateusercsv_task
from contentcuration.utils.csv_writer import generate_user_csv_filename
from contentcuration.utils.google_drive import add_row_to_sheet
from contentcuration.utils.messages import get_messages

ISSUE_UPDATE_DATE = datetime(2018, 10, 29)

CURRENT_USER = "current_user"
MESSAGES = "i18n_messages"


@login_required
@browser_is_supported
@has_accepted_policies
def settings(request):
    current_user = json_for_parse_from_serializer(UserSettingsSerializer(request.user))

    return render(
        request,
        'settings.html',
        {
            CURRENT_USER: current_user,
            MESSAGES: json_for_parse_from_data(get_messages()),
        },
    )


@login_required
@api_view(['GET'])
def export_user_data(request):
    generateusercsv_task.delay(request.user.pk)
    return HttpResponse({"success": True})


class PostFormMixin(LoginRequiredMixin):
    http_method_names = ['post']
    success_url = reverse_lazy('settings')

    def get_form(self, data):
        return self.form_class(data)

    def post(self, request):
        data = json.loads(request.body)
        form = self.get_form(data)
        if form.is_valid():
            self.form_valid(form)
            return HttpResponse()
        return HttpResponseBadRequest()


class UsernameChangeView(PostFormMixin, FormView):
    form_class = UsernameChangeForm

    def form_valid(self, form):
        form.save(self.request.user)


class UserPasswordChangeView(PostFormMixin, PasswordChangeView):
    form_class = SetPasswordForm

    def get_form(self, data):
        return self.form_class(self.request.user, data)


class IssuesSettingsView(PostFormMixin, FormView):
    form_class = IssueReportForm

    def form_valid(self, form):
        message = render_to_string('settings/issue_report_email.txt', {"data": form.cleaned_data, "user": self.request.user})
        send_mail(_("Kolibri Studio Issue Report"), message, ccsettings.DEFAULT_FROM_EMAIL, [ccsettings.HELP_EMAIL, self.request.user.email])


class DeleteAccountView(PostFormMixin, FormView):
    form_class = DeleteAccountForm

    def get_form(self, data):
        return self.form_class(self.request.user, data)

    def form_valid(self, form):
        # Send email to notify team about account being deleted
        buffer_date = (date.today() + timedelta(days=ccsettings.ACCOUNT_DELETION_BUFFER)).strftime('%A, %B %d %Y')
        subject = "Kolibri Studio account deleted"
        message = render_to_string('settings/account_deleted_notification_email.txt', {"user": self.request.user, "buffer_date": buffer_date})
        send_mail(subject, message, ccsettings.DEFAULT_FROM_EMAIL, [ccsettings.REGISTRATION_INFORMATION_EMAIL])

        # Send email to user regarding account deletion
        site = get_current_site(self.request)
        subject = _("Kolibri Studio account deleted")
        message = render_to_string('settings/account_deleted_user_email.txt', {
            "user": self.request.user,
            "buffer_date": buffer_date,
            "legal_email": ccsettings.POLICY_EMAIL,
            "num_days": ccsettings.ACCOUNT_DELETION_BUFFER,
            "site_name": site and site.name,
        })
        send_mail(subject, message, ccsettings.DEFAULT_FROM_EMAIL, [ccsettings.REGISTRATION_INFORMATION_EMAIL])

        # Delete user csv files
        csv_path = generate_user_csv_filename(self.request.user)  # Remove any generated csvs
        if os.path.exists(csv_path):
            os.unlink(csv_path)

        self.request.user.delete()


class StorageSettingsView(PostFormMixin, FormView):
    form_class = StorageRequestForm

    def form_valid(self, form):
        # Send email with storage request
        # name, email, storage requested, date of request, number of resources,
        # average resource size, kind of content, licenses, potential public
        # channels, audience, uploading for, message, time constraint
        values = [
            "{} {}".format(self.request.user.first_name, self.request.user.last_name),
            self.request.user.email,
            form.cleaned_data.get('storage'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            form.cleaned_data.get('resource_count'),
            form.cleaned_data.get('resource_size'),
            form.cleaned_data.get('kind'),
            form.cleaned_data.get('creators'),
            form.cleaned_data.get('sample_link'),
            form.cleaned_data.get('license'),
            form.cleaned_data.get("public"),
            form.cleaned_data.get('audience'),
            form.cleaned_data.get('location'),
            form.cleaned_data.get('import_count'),
            form.cleaned_data.get('uploading_for'),
            form.cleaned_data.get('organization_type'),
            form.cleaned_data.get('message'),
            form.cleaned_data.get('time_constraint'),
        ]
        # Write to storage request sheet
        # In production: https://docs.google.com/spreadsheets/d/1uC1nsJPx_5g6pQT6ay0qciUVya0zUFJ8wIwbsTEh60Y/edit#gid=0
        # Debug mode: https://docs.google.com/spreadsheets/d/16X6zcFK8FS5t5tFaGpnxbWnWTXP88h4ccpSpPbyLeA8/edit#gid=0
        add_row_to_sheet(ccsettings.GOOGLE_STORAGE_REQUEST_SHEET, values)

        channels = [c for c in form.cleaned_data['public'].split(', ') if c]
        message = render_to_string('settings/storage_request_email.txt', {"data": form.cleaned_data, "user": self.request.user, "channels": channels})
        send_mail("Kolibri Studio Storage Request", message, ccsettings.DEFAULT_FROM_EMAIL, [ccsettings.SPACE_REQUEST_EMAIL, self.request.user.email])


class PolicyAcceptView(LoginRequiredMixin, FormView):
    success_url = reverse_lazy('channels')
    form_class = PolicyAcceptForm
    template_name = 'policies/policy_accept.html'

    def get_context_data(self, **kwargs):
        kwargs = super(PolicyAcceptView, self).get_context_data(**kwargs)
        policies = json.loads(self.request.session.get('policies', "[]"))
        kwargs.update({"policies": policies})
        return kwargs

    def form_valid(self, form):
        form.save(self.request.user)
        self.request.session["policies"] = None
        return redirect(self.success_url)
