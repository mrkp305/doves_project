from datetime import datetime, date
import re

from django.db import models
from django.core.validators import ValidationError, RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.timesince import timesince
from django.urls import reverse

from model_utils.models import TimeStampedModel

from policies.models import Policy


class Member(TimeStampedModel):

    MALE = 'M'
    FEMALE = 'F'
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    MARRIED = 'M'
    SINGLE = 'S'
    DIVORCED = 'D'
    WIDOWED = 'W'
    MARITAL_STATUSES = (
        (MARRIED, "Married"),
        (SINGLE, 'Single'),
        (DIVORCED, 'Divorced'),
        (WIDOWED, 'Widowed'),
    )

    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name=_("User account"),
        on_delete=models.SET_NULL, editable=False,
        related_name="record", help_text=_("User account.")
    )
    first_name = models.CharField(
        verbose_name=_("First name"), max_length=255,
        help_text=_("Member's first name(s)."),
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=255,
        help_text=_("Member's last name.")
    )
    email_address = models.EmailField(
        verbose_name=_("Email address"), unique=True, help_text=_("Member email address"),
    )
    national_id = models.CharField(
        verbose_name=_("National ID"), max_length=12,
        help_text=_("National ID number."),
        validators=[
            RegexValidator(
                regex=r'\d{2}\d{6,7}[a-zA-Z]{1}\d{2}',
                message='ID Number should match format like: 58 398766 B 25, without the spaces.',
            )
        ]
    )
    date_of_birth = models.DateField(
        verbose_name=_("Date of birth"),
        help_text=_("Member's date of birth.")
    )
    sex = models.CharField(
        verbose_name=_("Sex"), max_length=1,
        choices=SEX_CHOICES,
        help_text=_("Member's sex orientation.")
    )
    date_joined = models.DateField(
        verbose_name=_("Date joined"),
        help_text=_("Date when member signed up for policy.")
    )
    policy = models.ForeignKey(
        Policy, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Policy"),
        related_name="members", help_text=_("Policy signed up for.")
    )
    marital_status = models.CharField(
        verbose_name=_("Marital status"), max_length=1,
        choices=MARITAL_STATUSES, default=MARRIED, help_text=_("Member's marital status.")
    )

    class Meta:
        verbose_name_plural = _("Members")

    def __str__(self):
        return f"{self.full_name}, {self.sex}".title()

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}".title()
    full_name.fget.short_description = _("Full name(s)")

    @property
    def marital_status_display(self):
        return self.get_marital_status_display()
    marital_status_display.fget.short_description = _("Marital Status")

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year - \
            ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age
    age.fget.short_description = _("Age")

    @property
    def dependant_count(self):
        return self.dependants.count()
    dependant_count.fget.short_description = _("Dependants")

    @property
    def dependant_count_percentage(self):
        return (self.dependant_count/self.policy.dependants_per_holder) * 100

    @property
    def claim_count(self):
        return Claim.objects.filter(dependant__member=self).count()
    claim_count.fget.short_description = _("Claims made")

    @property
    def claims(self):
        return Claim.objects.filter(dependant__member=self)

    @property
    def last_claim_date(self):
        try:
            return Claim.objects.filter(dependant__member=self).order_by('-date_of_claim')[0]
        except:
            return None
    last_claim_date.fget.short_description = _("Last claim")

    @property
    def days_since_last_claim(self):
        if self.last_claim_date is None:
            return (datetime.now().date() - self.date_joined).days
        else:
            return (datetime.now().date() - self.last_claim_date.date_of_claim).days

    @property
    def days_since_last_cashback(self):
        if self.last_cashback_date is not None:
            return (datetime.now().date() - self.last_cashback_date.created.date()).days
        else:
            return (datetime.now().date() - self.date_joined).days

    @property
    def last_cashback_date(self):
        try:
            return self.cashback_records.order_by('-created')[0]
        except:
            return None

    @property
    def cash_back_eligible(self):
        if (self.days_since_last_cashback >= self.policy.cash_back_days) and (self.days_since_last_claim >= self.policy.cash_back_days):
            return True
        return False
    cash_back_eligible.fget.short_description = _("Cash back eligibile?")

    def clean(self):
        super(Member, self).clean()
        regex = re.compile(r'^[a-zA-Z\']+$', re.U)
        if not regex.match(self.first_name):
            raise ValidationError({"first_name": 'Invalid name'})

        if not regex.match(self.last_name):
            raise ValidationError({"last_name": 'Invalid name'})

        if self.date_of_birth:
            if self.date_of_birth > datetime.now().date():
                raise ValidationError(_("Date of birth cannot be greater than today's date."))
            else:
                if self.age < 16:
                    raise ValidationError(
                        {'date_of_birth': _("Policy holders can only be 16 years and older.")}
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Member, self).save(*args, **kwargs)


class Dependant(TimeStampedModel):

    CHILD = "C"
    SPOUSE = "S"
    OTHER = "O"
    RELATIONSHIP_CHOICES = (
        (CHILD, "Child"),
        (SPOUSE, "Spouse"),
        (OTHER, "Other"),
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, verbose_name=_("Member"),
        related_name="dependants", help_text=_("Reference to policy registrant.")
    )
    relationship = models.CharField(
        verbose_name=_("Relationship"), max_length=1,
        choices=RELATIONSHIP_CHOICES, help_text=_("Relationship to policy registrant.")
    )
    relationship_description = models.TextField(
        verbose_name=_("Relationship description"), null=True, blank=True,
        help_text=_("If relationship is indicated as other, please explain relationship to dependant here.")
    )
    first_name = models.CharField(
        verbose_name=_("First name"), max_length=255,
        help_text=_("Dependant's first name(s).")
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=255,
        help_text=_("Dependant's last name.")
    )
    date_of_birth = models.DateField(
        verbose_name=_("Date of birth"),
        help_text=_("Dependant's date of birth.")
    )
    sex = models.CharField(
        verbose_name=_("Sex"), max_length=1,
        choices=Member.SEX_CHOICES,
        help_text=_("Dependant's sex orientation.")
    )
    date_joined = models.DateField(
        verbose_name=_("Date joined"),
        help_text=_("Date when dependant was registered.")
    )
    is_deceased = models.BooleanField(
        verbose_name=_("Deceased"), default=False, editable=False,
        help_text=_("Mark dependant as deceased.")
    )

    class Meta:
        verbose_name = _("Dependant")
        verbose_name_plural = _("Dependants")

    def __str__(self):
        return f"{self.full_name}, {self.sex}".title()

    def get_absolute_url(self):
        return reverse('members:view_dependant', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}".title()
    full_name.fget.short_description = _("Full name(s)")

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age
    age.fget.short_description = _("Age")

    @property
    def relationship_display(self):
        return self.get_relationship_display()
    relationship_display.fget.short_description = _("Relationship")

    @property
    def member_name(self):
        return self.member.full_name
    member_name.fget.short_description = _("Policy holder")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        regex = re.compile(r'^[a-zA-Z\']+$', re.U)
        if not regex.match(self.first_name):
            raise ValidationError({"first_name": 'Invalid name'})

        if not regex.match(self.last_name):
            raise ValidationError({"last_name": 'Invalid name'})

        if self.date_of_birth:
            if self.date_of_birth > datetime.now().date():
                raise ValidationError(
                    {'date_of_birth': _("Date of birth cannot be greater than today's date.")}
                )

        if self.relationship == "O" and (self.relationship_description is None or self.relationship_description == ""):
            raise ValidationError(
                {'relationship_description': _("Explain the relationship with dependant."), }
            )

        if not self.pk:
            # Validate dependant count
            if self.member.policy is None:
                raise ValidationError(
                    _("%(member)s has not been registered for a policy yet."),
                    params={
                        'member': self.member.full_name,
                    }
                )
            else:
                policy = self.member.policy
                if self.member.dependant_count + 1 > policy.dependants_per_holder:
                    raise ValidationError(
                        _("You can only have %(dependants)s dependants under the %(policy)s policy."),
                        params={
                            'dependants': policy.dependants_per_holder,
                            'policy': policy.name.title(),
                        }
                    )
            super(Dependant, self).clean()


class Claim(TimeStampedModel):

    dependant = models.OneToOneField(
        Dependant, on_delete=models.CASCADE, verbose_name=_("Dependant reference."),

    )

    date_of_claim = models.DateField(
        verbose_name=_("Date of claim"),
        help_text=_("Date when claim was made.")
    )

    place_of_death = models.CharField(
        verbose_name=_("Place of death"), max_length=255,
        help_text=_("Place where policy dependant died.")
    )

    date_of_death = models.DateField(
        verbose_name=_("Date of death"),
        help_text=_("Date when the deceased died as reflected on death certificate.")
    )

    class Meta:
        verbose_name_plural = _('Claims')

    def __str__(self):
        return f"Dependant #{self.dependant.id} - {self.dependant}"

    def clean(self):
        super(Claim, self).clean()
        if self.date_of_death:
            if self.date_of_death > datetime.now().date():
                raise ValidationError(
                    {
                        'date_of_death': "Date of death cannot be greater than today's date!"
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Claim, self).save(*args, **kwargs)
        self.dependant.is_deceased = True
        self.dependant.save()


class Request(TimeStampedModel):
    first_name = models.CharField(
        verbose_name=_("First name"), max_length=255,
        help_text=_("Client first name(s).")
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=255,
        help_text=_("Client's last name.")
    )
    national_id = models.CharField(
        verbose_name=_("National ID"), max_length=12,
        help_text=_("Client National ID number."),
        validators=[
            RegexValidator(
                regex=r'\d{2}\d{6,7}[a-zA-Z]{1}\d{2}',
                message='ID Number should match format like: 58 398766 B 25, without the spaces.',
            )
        ]
    )
    email_address = models.EmailField(
        verbose_name=_("Email Address"), max_length=255,
        help_text=_("Client's email address"),
    )
    phone = models.CharField(
        verbose_name=_("Phone number"), max_length=10,
        help_text=_("Client's contact phone number.")
    )
    sex = models.CharField(
        verbose_name=_("Sex"), max_length=1,
        choices=Member.SEX_CHOICES,
        help_text=_("Client's sex orientation.")
    )
    address = models.TextField(
        verbose_name=_("Address"), max_length=255,
        help_text=_("Address where services are required.")
    )
    details = models.TextField(
        verbose_name=_("Details"), max_length=1000,
        help_text=_("Detailed description of required services or assistance.")
    )
    lat = models.CharField(
        verbose_name=_("Latitude"), max_length=255,
        help_text=_("Latitude coordinate.")
    )
    lng = models.CharField(
        verbose_name=_("Longitude"), max_length=255,
        help_text=_("Longitude coordinate.")
    )
    deceased_death_certificate = models.FileField(
        verbose_name=_("Deceased's death certificate"), upload_to="requests/certs/",
    )

    class Meta:
        verbose_name_plural = _("Requests")

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def requested(self):
        return f"{timesince(self.created)} ago"
    requested.fget.short_description = _("Requested")

    @property
    def coordinates(self):
        return f"{self.lat, self.lng}"

    @property
    def paid_for(self):
        if hasattr(self, "payments"):
            for payment in self.payments.all():
                if payment.transaction.completed:
                    return True
        return False
    paid_for.fget.short_description = _("Paid For")

    def get_absolute_url(self):
        return reverse(
            'view_request', kwargs={
                'pk': self.pk,
            }
        )

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}".title()
    full_name.fget.short_description = _("Full name(s)")


class Cashback(TimeStampedModel):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, verbose_name=_("Member"),
        related_name="cashback_records", help_text=_("Member reference.")
    )

    amount = models.DecimalField(
        verbose_name=_("Amount"), max_digits=19, decimal_places=4, help_text=_("Amount Requested"),
    )

    paid_out = models.BooleanField(
        verbose_name=_("Paid out"), default=False, help_text=_("Paid out?"),
    )

    class Meta:
        verbose_name = _("Cash back request")
        verbose_name_plural = _("Cash back requests")


class TransactionManager(models.Manager):
    """Custom manager to Transactions
    """

    def create_transaction(self, **kwargs):
        try:
            trans = self.model(**kwargs)
        except Exception as ex:
            # TODO: Log error
            return None
        else:
            trans.save(using=self._db)
            return trans


class Transaction(TimeStampedModel):
    """Repr(s) a transaction involving payments
    Based on Paynow
    """
    poll_url = models.URLField(null=True, blank=True, editable=False)
    url = models.URLField(null=True, blank=True, editable=False)
    reference = models.CharField(
        verbose_name=_("Reference"), max_length=255, null=True, blank=True,
    )
    # Value is the amount expected to be paid
    value = models.DecimalField(verbose_name=_("Value"), max_digits=19,
                                decimal_places=2, editable=False)
    # Amount paid is the actual amount paid as returned
    # by Paynow
    paid = models.DecimalField(verbose_name=_("Amount paid"), max_digits=19,
                               decimal_places=2, null=True, blank=True, editable=False)
    completed = models.BooleanField(
        default=False, verbose_name=_("Indicates if transaction was complete"), editable=False
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ("-created", )

    def complete(self):
        if not self.paid:
            return
        self.completed = True
        self.save()
        return 1


class RequestPayment(TimeStampedModel):

    request = models.ForeignKey(
        to=Request, on_delete=models.CASCADE, related_name="payments",
    )
    transaction = models.ForeignKey(
        to=Transaction, on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Request Payment")
        verbose_name_plural = _("Request Payments")
