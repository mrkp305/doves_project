from django.db import models
from django.utils.translation import ugettext_lazy as _


class Policy(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, unique=True,
        help_text=_("Policy name.")
    )
    description = models.TextField(
        verbose_name=_("Description"), max_length=500,
        help_text=_("Policy description.")
    )
    dependants = models.PositiveSmallIntegerField(
        verbose_name=_("Dependants"), default=1,
        help_text=_("Number of dependants covered.")
    )

    class Meta:
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")

    def __str__(self):
        return str(self.name)