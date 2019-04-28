# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils.translation import ugettext_lazy as _
#
#
# class User(AbstractUser):
#     username = None
#     email = models.EmailField(_("email address"), max_length=254, unique=True)
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     def __str__(self):
#         return "{} {}".format(self.first_name, self.last_name)