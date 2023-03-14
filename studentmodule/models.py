from django.db import models
from core.models import User
from programmodule.models import Programs
from django.utils.translation import gettext_lazy as _
import datetime


# Create your models here.

def student_images(instance, filename):
    return '/'.join(['StudentImages', str(instance.id), filename])


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentuser')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='studentprogram')
    firstname = models.CharField(default="", max_length=255, blank=False, null=False)
    lastname = models.CharField(default="", max_length=255, blank=False, null=False)
    marital_status = models.CharField(default="", max_length=255, blank=False, null=False)
    cnic = models.CharField(default='', max_length=255, blank=False, null=False)
    phone_number = models.CharField(default='', max_length=255, blank=False, null=False)
    province = models.CharField(default='', max_length=255, blank=False, null=False)
    roll_number = models.CharField(default='', max_length=255, blank=False, null=False)
    address = models.CharField(max_length=255, null=False, blank=False, default='')
    batch = models.CharField(max_length=255, null=False, blank=False, default='')
    degree = models.CharField(max_length=255, null=False, blank=False, default='')
    dob = models.DateField(null=False, blank=False)
    domicile = models.CharField(max_length=255, null=False, blank=False, default='')
    gender = models.CharField(max_length=255, null=False, blank=False, default='')
    institute = models.CharField(max_length=255, null=False, blank=False, default='')
    image = models.ImageField(upload_to=student_images, max_length=254, blank=True, null=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
