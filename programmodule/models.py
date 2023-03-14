from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from studentmodule.models import *
import datetime


def program_images(instance, filename):
    return '/'.join(['ProgramImages', str(instance.id), filename])


def course_images(instance, filename):
    return '/'.join(['CourseImages', str(instance.id), filename])


# Create your models here.
class Programs(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = HTMLField()
    image = models.ImageField(upload_to=program_images, max_length=254, blank=True, null=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)


class Course(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='courseprogram')
    description = HTMLField()
    image = models.ImageField(upload_to=course_images, max_length=254, blank=True, null=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)


class CourseContent(models.Model):
    TYPE_ROLE_CHOICES = (
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('ASSIGNMENT', 'Assignment'),
    )
    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, choices=TYPE_ROLE_CHOICES, blank=False, null=False)
    url = models.URLField(max_length=255, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='coursecontent')
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
