from django.db import models
from core.models import User
from django.utils.translation import gettext_lazy as _
import datetime


def admin_images(instance, filename):
    return '/'.join(['AdminImages', str(instance.id), filename])


# Create your models here.
class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminuser')
    firstname = models.CharField(default="", max_length=255, blank=False, null=False)
    lastname = models.CharField(default="", max_length=255, blank=False, null=False)
    cnic = models.CharField(default='', max_length=255, blank=True, null=True)
    phone_number = models.CharField(default='', max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=admin_images, max_length=254, blank=True, null=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
