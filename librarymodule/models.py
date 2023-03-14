from django.db import models
from tinymce.models import HTMLField
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
import datetime


# Create your models here.
def publication_images(instance, filename):
    return '/'.join(['PublicationImages', str(instance.id), filename])


def publication_files(instance, filename):
    return '/'.join(['PublicationFiles', str(instance.id), filename])


def resource_images(instance, filename):
    return '/'.join(['ResourceImages', str(instance.id), filename])


def resource_files(instance, filename):
    return '/'.join(['ResourceFiles', str(instance.id), filename])


def library_files(instance, filename):
    return '/'.join(['LibraryFiles', str(instance.id), filename])


def library_images(instance, filename):
    return '/'.join(['LibraryImages', str(instance.id), filename])


class Library(models.Model):
    LIBRARY_TYPES = (
        ('Book', 'Book'),
        ('Magazines', 'Magazines'),
        ('Multimedia', 'Multimedia'),
        ('Others', 'Others'),
    )
    title = models.CharField(max_length=255, null=False, blank=False, default='')
    description = HTMLField()
    url = models.URLField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, choices=LIBRARY_TYPES, null=False, blank=False)
    image = models.ImageField(upload_to=library_images, max_length=254, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    file = models.FileField(upload_to=library_files, max_length=254, null=True, blank=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)


class Publication(models.Model):
    PUBLICATION_CHOICES = (
        ('Book', 'Book'),
        ('Magazines', 'Magazines'),
        ('Multimedia', 'Multimedia'),
        ('Others', 'Others'),
    )
    title = models.CharField(max_length=255, null=False, blank=False, default='')
    description = HTMLField()
    url = models.URLField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, choices=PUBLICATION_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to=publication_images, max_length=254, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=512), null=True, blank=True)
    file = models.FileField(upload_to=publication_files, max_length=254, null=True, blank=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)


class Resources(models.Model):
    RESOURCES_TYPES = (
        ('Video', 'Video'),
        ('Audio', 'Audio'),
        ('Document', 'Document'),
    )
    title = models.CharField(max_length=255, null=False, blank=False, default='')
    description = HTMLField()
    url = models.URLField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, choices=RESOURCES_TYPES, null=True, blank=True)
    image = models.ImageField(upload_to=resource_images, max_length=254, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=512), null=True, blank=True)
    file = models.FileField(upload_to=resource_files, max_length=254, null=True, blank=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
