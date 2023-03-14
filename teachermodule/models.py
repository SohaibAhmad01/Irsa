from django.db import models
from core.models import User
from django.utils.translation import gettext_lazy as _
import datetime


# Create your models here.
def teacher_images(instance, filename):
    return '/'.join(['TeacherImages', str(instance.id), filename])


class Teacher(models.Model):
    TEACHER_STATUS = (
        ('Current', 'Current'),
        ('Retired', 'Retired')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacheruser')
    firstname = models.CharField(default="", max_length=255, blank=False, null=False)
    lastname = models.CharField(default="", max_length=255, blank=False, null=False)
    cnic = models.CharField(default='', max_length=255, blank=True, null=True)
    phone_number = models.CharField(default='', max_length=255, blank=True, null=True)
    designation = models.CharField(default='', max_length=255, blank=True, null=True)
    qualification = models.CharField(default='', max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=teacher_images, max_length=254, blank=True, null=True)
    status = models.CharField(max_length=255, choices=TEACHER_STATUS, blank=False, null=False, default='Current')
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
