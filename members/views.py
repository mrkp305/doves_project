import unicodedata

from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import (
    render,
)

from .forms import RegisterForm, AuthenticationForm


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


class Profile(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile.html'

    def test_func(self):
        return self.request.user.member is not None

profile_view = Profile.as_view()
