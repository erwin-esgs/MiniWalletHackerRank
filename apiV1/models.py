from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    guid = models.CharField(primary_key=True,max_length=36)
    last_check = models.IntegerField(_('last check') ,default=0)
    is_enabled = models.BooleanField(default=False)
    enabled_at = models.IntegerField(_('enabled at') ,default=None, blank=True, null=True)
    disabled_at = models.IntegerField(_('disabled at') ,default=None, blank=True, null=True)
    USERNAME_FIELD = 'username'

class Transaction(models.Model):
    guid = models.CharField(primary_key=True,max_length=36)
    timestamp = models.IntegerField()
    reference_id = models.CharField(max_length=36)
    by = models.CharField(max_length=36)
    type = models.CharField(max_length=12)
    amount = models.IntegerField()
    