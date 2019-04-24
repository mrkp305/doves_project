from datetime import datetime, date

from django.db import models
from django.core.validators import ValidationError, RegexValidator
from django.utils.translation import ugettext_lazy as _

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

    first_name = models.CharField(
        verbose_name=_("First name"), max_length=255,
        help_text=_("Member's first name(s).")
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=255,
        help_text=_("Member's last name.")
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
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age
    age.fget.short_description = _("Age")
    
    @property
    def dependant_count(self):
        return self.dependants.count()
    dependant_count.fget.short_description = _("Dependants")

    def clean(self):
        super(Member, self).clean()
        if self.date_of_birth > datetime.now().date():
            raise ValidationError(_("Date of birth cannot be greater than today's date."))
        else:
            if self.age < 16:
                raise ValidationError(_("Policy holders can only be 16 years and older."))

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

    class Meta:
        verbose_name = _("Dependant")
        verbose_name_plural = _("Dependants")

    def __str__(self):
        return f"{self.full_name}, {self.sex}".title()

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
        super(Dependant, self).clean()
        if self.date_of_birth > datetime.now().date():
            raise ValidationError(
                {'date_of_birth': _("Date of birth cannot be greater than today's date.")}
            )

        if self.relationship == "O" and (self.relationship_description is None or self.relationship_description == ""):
            raise ValidationError(
                {'relationship_description': _("Explain the relationship with dependant."),}
            )

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
            if self.member.dependant_count >= policy.dependants_per_holder:
                raise ValidationError(
                    _("You can only have %(dependants)s dependants under the %(policy)s policy."),
                    params={
                        'dependants': policy.dependants_per_holder,
                        'policy': policy.name.title(),
                    }
                )
