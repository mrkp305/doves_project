import re

from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _

def national_id_validator(value):
    regex_string = re.compile(r'\d{2}\d{6,7}[a-zA-Z]{1}\d{2}', re.IGNORECASE)
    if not regex_string.match(value):
        raise ValidationError(
            _("Value does not match required format: e.g 57 833388(8) A 20, without the spaces.")
        )