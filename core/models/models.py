from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
import datetime


def news_images(instance, filename):
    return '/'.join(['NewsImages', str(instance.id), filename])


def course_images(instance, filename):
    return '/'.join(['CourseImages', str(instance.id), filename])


# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('teacher', 'teacher'),
        ('student', 'student'),
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=False, null=False, default='')
    """User model."""
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return self.email


class OtpTemp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otpuser')
    otp = models.CharField(max_length=255, default='', blank=True, null=True)
    generated_time = models.DateTimeField(null=True, blank=True)


class News(models.Model):
    NEWS_CHOICE = (
        ('News', 'News'),
        ('Event', 'Event'),
    )
    title = models.CharField(max_length=255, null=False, blank=False, default='')
    description = HTMLField()
    type = models.CharField(max_length=255, choices=NEWS_CHOICE, null=True, blank=True)
    image = models.ImageField(upload_to=news_images, max_length=254, blank=True, null=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
