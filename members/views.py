import datetime
import requests
from six.moves.urllib_parse import quote_plus, parse_qs

from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

from django.shortcuts import get_object_or_404, render, reverse

from paynow import Paynow, StatusResponse

from .forms import (
    RegisterForm, AuthenticationForm, MemberForm, DependantForm,
    ClaimForm, CashbackForm, RequestForm
)
from .models import Member, Dependant, Claim, Cashback, Request, Transaction, RequestPayment


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class Register(generic.edit.FormView, generic.View):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("members:login")

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        return HttpResponseRedirect(self.get_success_url())


register_view = Register.as_view()


class Login(auth_views.LoginView):
    template_name = "login.html"
    form_class = AuthenticationForm


login_view = Login.as_view()


class Profile(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView, generic.View):
    template_name = 'profile.html'
    form_class = MemberForm
    success_url = reverse_lazy('members:profile')

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get_object(self, queryset=None):
        return self.request.user.record

    def form_valid(self, form):
        messages.success(request=self.request, message="Account Information updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request,
                       message="There was an error upadting your account, please check the form and try again.")
        return super(Profile, self).form_invalid(form)


profile_view = Profile.as_view()


class AddDependant(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    form_class = DependantForm
    template_name = "add_dependant.html"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def form_valid(self, form):
        form.instance.member = self.request.user.record
        form.instance.date_joined = datetime.datetime.now().date()
        return super(AddDependant, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request, message="Please correct the errors below.")
        return super(AddDependant, self).form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        self.initial['member'] = self.request.user.record
        return super(AddDependant, self).dispatch(request, *args, **kwargs)


add_dependant_view = AddDependant.as_view()


class ViewDependant(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    template_name = "dependant.html"
    model = Dependant


view_dependant_view = ViewDependant.as_view()


class EditDependant(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Dependant
    form_class = DependantForm
    template_name = "edit_dependant.html"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def form_valid(self, form):
        messages.success(request=self.request, message="Dependant record successfully updated.")
        return super(EditDependant, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request,
                       message="Action failed. Please check the form below and try again.")
        return super(EditDependant, self).form_invalid(form)


edit_dependant_view = EditDependant.as_view()


class DeleteDependant(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    template_name = "delete_dependant.html"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get(self, request, pk):
        d = Dependant.objects.get(pk=pk)
        d.delete()
        messages.success(request=self.request, message="Dependant successfully removed.")
        return HttpResponseRedirect(reverse_lazy('members:dependants'))


delete_dependant_view = DeleteDependant.as_view()


class Dependants(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Dependant
    context_object_name = 'dependants'
    template_name = "dependants.html"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get_queryset(self, **kwargs):
        return Dependant.objects.filter(member=self.request.user.record)


dependants_view = Dependants.as_view()


class ClaimCover(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    form_class = ClaimForm
    template_name = "claim.html"
    success_url = reverse_lazy("members:claims")

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get_context_data(self, **kwargs):
        c = super(ClaimCover, self).get_context_data(**kwargs)
        c["dependant"] = self.request.user.record.dependants.get(pk=self.kwargs['dependant'])
        return c

    def form_valid(self, form):
        form.instance.dependant = Dependant.objects.get(pk=self.kwargs['dependant'])
        messages.success(request=self.request, message="Claim send")
        return super(ClaimCover, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request,
                       message="Failed to submit claim. Please check form and try again.")
        return super(ClaimCover, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.initial['dependant'] = self.request.user.record.dependants.get(
            pk=self.kwargs['dependant'])
        self.initial['date_of_claim'] = datetime.datetime.now().date()
        return super().get(self.request, *args, **kwargs)


claim_cover_view = ClaimCover.as_view()


class Claims(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Claim
    template_name = "claims.html"
    context_object_name = "claims"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get_queryset(self):
        return self.request.user.record.claims


claims_view = Claims.as_view()


class Cashbacks(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Cashback
    template_name = "cashbacks.html"
    context_object_name = "cashbacks"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get_queryset(self):
        return self.request.user.record.cashback_records.all()


cashbacks_view = Cashbacks.as_view()


class CashbackRequest(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    template_name = "cashback.html"
    success_url = reverse_lazy("members:cashbacks")
    form_class = CashbackForm

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def form_valid(self, form):
        messages.success(request=self.request, message="Cashback request sent.")
        return super(CashbackRequest, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request, message="Failed to sent request, please check form.")
        return super(CashbackRequest, self).form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        self.initial['member'] = self.request.user.record
        return super().dispatch(request, *args, **kwargs)


cash_request_view = CashbackRequest.as_view()


class DeleteCashBack(LoginRequiredMixin, UserPassesTestMixin, generic.View):

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False

    def get(self, request, pk):
        Cashback.objects.get(pk=pk).delete()
        return HttpResponseRedirect(reverse_lazy('members:cashbacks'))


delete_cash_back_view = DeleteCashBack.as_view()


class Index(generic.TemplateView):
    template_name = "home.html"


index_view = Index.as_view()


class InstantCover(generic.CreateView):
    template_name = "instant.html"
    form_class = RequestForm

    def get_success_url(self):
        return reverse("pay_request", kwargs={"pk": self.object.pk})


instant_cover_view = InstantCover.as_view()


class Payment(generic.DetailView):
    template_name = "payment.html"
    model = Request
    context_object_name = 'request'

    def dispatch(self, request, *args, **kwargs):
        re = self.get_object()
        if re.paid_for:
            return HttpResponse("This instant cover request has been paid for already. Our agents will contact you soon.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return_url = f"http://localhost:8000/"
        result_url = f"http://localhost:8000/"

        self.req = self.get_object()
        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            return_url=return_url,
            result_url=result_url,
        )

        # Create payment ref
        payment = paynow.create_payment(
            f"Doves Instant Cover Request Fee for request #{self.req.id} ({self.req.full_name})",
            self.req.email_address if self.req.email_address else None
        )
        del payment.items[:]  # Clear items # Apprently had to clear on every request.
        # Add items(Reg. fees)
        payment.add('Instant Cover Request Fee', settings.REQUEST_FEE)
        # Save the response from paynow in a variable
        response = paynow.send(payment)
        if response.success:
            # URL from Paynow to poll for status
            self.poll_url = response.poll_url
            # Payment URL to redirect user to
            self.link = response.redirect_url
            # Create paynow transaction in db
            self.trans = Transaction.objects.create(
                poll_url=self.poll_url, url=self.link, value=settings.REQUEST_FEE, reference=f"Instant Cover request fee for request #{self.req.id}({self.req.full_name})")
            RequestPayment.objects.create(
                request=self.req,
                transaction=self.trans,
            )
            self.plus_context = {
                "transaction": self.trans,
                "proceed": reverse_lazy("succ")
            }
            paynow = None
            payment = None
            response = None
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponse("Failed to contact the Paynow servers, please try again later.")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update(self.plus_context)
        return c


payment_view = Payment.as_view()


class TransactionStatus(generic.View):

    def get(self, request, **kwargs):
        # Ajax response to return after checking
        ajax_response = dict()

        # Get Transaction
        trans = get_object_or_404(Transaction, id=kwargs["pk"])
        # Get poll url
        poll_url = trans.poll_url
        if poll_url:
            response = requests.post(poll_url, {})
            if response.status_code == 200:
                # Get query string from response
                response_qs = parse_qs(response.text)
                # create_holding_dict
                res = dict()
                # loop query string
                for key, value in response_qs.items():
                    res.update({key: str(value[0])})
                status = StatusResponse(res, False)  # Get StatusResponse object from Paynow
                if status.paid:
                    trans.paid = status.amount
                    trans.save()
                    trans.complete()  # Mark transaction as complete
                    ajax_response.update({"complete": 1, "status": status.status})
                else:
                    ajax_response.update({"complete": 0, "status": status.status})

            else:
                # TODO: Log errors
                ajax_response.update(
                    {"complete": 0, "status": "Failed to check transation status."})
        else:
            # Send back fail
            ajax_response.update({"complete": 0, "status": "Transaction not valid"})
            # TODO: Add logging

        # Finally return ajax response
        return JsonResponse(ajax_response, safe=False)


transaction_check_view = TransactionStatus.as_view()


class ISucc(generic.TemplateView):
    template_name = "succ.html"


isucc_view = ISucc.as_view()


class ViReq(LoginRequiredMixin, generic.DetailView):
    model = Request
    template_name = "request.html"
    context_object_name = "request"


view_request_view = ViReq.as_view()


class HeAss(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = "heass.html"

    def test_func(self):
        try:
            r = self.request.user.record
            return True
        except Exception as ex:
            return False


heath_assessment_view = HeAss.as_view()
