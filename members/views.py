import datetime

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import RegisterForm, AuthenticationForm, MemberForm, DependantForm
from .models import Member, Dependant


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


class Profile(LoginRequiredMixin, generic.edit.UpdateView, generic.View):
    template_name = 'profile.html'
    form_class = MemberForm
    success_url = reverse_lazy('members:profile')

    def get_object(self, queryset=None):
        return self.request.user.record

    def form_valid(self, form):
        messages.success(request=self.request, message="Account Information updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request, message="There was an error upadting your account, please check the form and try again.")
        return super(Profile, self).form_invalid(form)

profile_view = Profile.as_view()


class AddDependant(generic.CreateView):
    form_class = DependantForm
    template_name = "add_dependant.html"

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


class ViewDependant(generic.DetailView):
    template_name = "dependant.html"
    model = Dependant

view_dependant_view = ViewDependant.as_view()


class EditDependant(generic.UpdateView):
    model = Dependant
    form_class = DependantForm
    template_name = "edit_dependant.html"

    def form_valid(self, form):
        messages.success(request=self.request, message="Dependant record successfully updated.")
        return super(EditDependant, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(request=self.request, message="Action failed. Please check the form below and try again.")
        return super(EditDependant, self).form_invalid(form)
edit_dependant_view = EditDependant.as_view()


class DeleteDependant(generic.View):
    template_name = "delete_dependant.html"

    def get(self, request, pk):
        d = Dependant.objects.get(pk=pk)
        d.delete()
        messages.success(request=self.request, message="Dependant successfully removed.")
        return HttpResponseRedirect(reverse_lazy('members:dependants'))

delete_dependant_view = DeleteDependant.as_view()


class Dependants(generic.ListView):
    model = Dependant
    context_object_name = 'dependants'
    template_name = "dependants.html"

dependants_view = Dependants.as_view()
