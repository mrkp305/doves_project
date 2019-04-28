from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

class Policy(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, unique=True,
        help_text=_("Policy name.")
    )
    description = models.TextField(
        verbose_name=_("Description"), max_length=500,
        help_text=_("Policy description.")
    )
    dependants_per_holder = models.PositiveSmallIntegerField(
        verbose_name=_("Dependants"), default=1,
        help_text=_("Number of dependants covered.")
    )
    cash_back_days = models.PositiveSmallIntegerField(
        verbose_name=_("Cash back days"), default=6,
        help_text=_("Indicate the number of days without claiming qualifies a cash back.")
    )

    class Meta:
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")

    def __str__(self):
        return str(self.name).title()

    @property
    def member_count(self):
        return self.members.count()
    member_count.fget.short_description = _("Policy holders")

    @property
    def dependant_count(self):
        from members.models import Dependant
        return Dependant.objects.filter(member__policy=self).count()
    dependant_count.fget.short_description = _("Dependants Registered Under Policy")
