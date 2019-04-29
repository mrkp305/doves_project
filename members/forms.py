import unicodedata

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.utils.text import capfirst
from django.contrib.auth import (
    authenticate,
)

from .models import Member, Dependant, Claim, Request, Cashback


User = get_user_model()


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label=_("Email address"), widget=forms.EmailInput(
            attrs={
                'class': 'form-control', 'placeholder': 'Email address'
            }
        ), help_text=_("Member's registered email address.")
    )
    national_id = forms.CharField(
        label=_("National ID"), widget=forms.TextInput(
            attrs={'class': 'form-control',}
        ), help_text=_("National ID Number as indicated on membership form."),
        validators=[
            RegexValidator(
                regex=r'\d{2}\d{6,7}[a-zA-Z]{1}\d{2}',
                message='ID Number should match format like: 58 398766 B 25, without the spaces.',
            )
        ]
    )
    username = forms.CharField(
        label=_("Username"), widget=forms.TextInput(
            attrs={'class': 'form-control',}
        ), help_text=_("Create a username for your account.")
    )
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput(
            attrs={'class': 'form-control',}
        ), help_text=_("Create account Password.")
    )
    password2 = forms.CharField(
        label=_("Confirm password"), widget=forms.PasswordInput(
            attrs={'class': 'form-control',}
        ), help_text=_("Repeat your password to confirm it.")
    )


    def clean(self):
        data = super().clean()
        email = data.get('email')
        national_id = data.get('national_id')
        password = data.get('password')
        password2 = data.get('password2')
        if len(password) < 6:
            self.add_error('password', "Password too short. Please enter at least 6 Characters.")
        else:
            if password != password2:
                self.add_error('password2', "Failed to confirm your password. Please try again.")

        if Member.objects.filter(email_address=email).count() < 1:
            self.add_error("email" , "No membership record found with that email!")
        else:
            if Member.objects.filter(email_address=email)[0].national_id != national_id:
                self.add_error(None, "Failed to find an account with such details. Please contact your branch")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', "Username already taken, please choose another.")
        else:
            if len(username) > 12:
                self.add_error("username", 'Username too long. Max: 12 Characters.')
        return username

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password')
        )
        if User.objects.filter(email=self.cleaned_data.get('email')).exists():
            pass
        else:
            user.email=self.cleaned_data.get('email')
            user.save()
        member = Member.objects.get(email_address=self.cleaned_data.get("email"))
        member.user_account = user
        member.save()
        return True


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ["first_name", "last_name", "email_address", "marital_status", ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'email_address': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            )
        }


class DependantForm(forms.ModelForm):

    class Meta:
        model = Dependant
        fields =["member", "first_name", "last_name", "sex", "date_of_birth", "relationship", "relationship_description", ]

        widgets = {
            'member': forms.HiddenInput(

            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'sex': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'relationship': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'relationship_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'cold': 30,
                }
            )
        }


class ClaimForm(forms.ModelForm):

    class Meta:
        fields = ['date_of_claim', 'place_of_death', 'date_of_death', ]
        model = Claim
        widgets = {
            'date_of_claim': forms.HiddenInput(),
            'place_of_death': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'date_of_death': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            )
        }


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ["first_name", "last_name", "sex", "email_address", "national_id", "address", "lat", "lng", "details", "phone", "deceased_death_certificate", ]
        widgets = {
            "lat": forms.HiddenInput(),
            "lng": forms.HiddenInput(),
            "first_name": forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            "email_address": forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            "sex": forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            "national_id": forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            "address": forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            "deceased_death_certificate": forms.FileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


class CashbackForm(forms.ModelForm):

    class Meta:
        model = Cashback
        fields = ['amount', 'member', ]
        widgets = {
            'member': forms.HiddenInput(),
            'amount': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '10.00',
                    'class': 'form-control',
                }
            )
        }


class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = UsernameField(label=_("Username"), widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control',}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',}
        ),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        self.fields['username'].max_length = self.username_field.max_length or 254
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )
