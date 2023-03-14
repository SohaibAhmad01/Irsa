from django.db import models
from teachermodule.models import Teacher
from programmodule.models import Course
from studentmodule.models import Student
import datetime
from core.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Class(models.Model):
    CLASS_STATUS = (
        ('active', 'active'),
        ('inactive', 'inactive'),
    )
    batch = models.CharField(max_length=255, blank=False, null=False, default='')
    startDate = models.DateField(blank=False, null=False)
    endDate = models.DateField(blank=False, null=False)
    title = models.CharField(max_length=255, blank=False, null=False, default='')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False,
                                related_name='classteacher')
    year = models.IntegerField(_('year'), null=True, blank=True, default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False,
                               related_name='courseteacher')
    status = models.CharField(max_length=255, choices=CLASS_STATUS, null=False, blank=False, default='inactive')
    student_list = models.ManyToManyField(Student, null=True, blank=True)
    created_at = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    created_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)


def get_time():
    return datetime.datetime.now()


class Message(models.Model):
    title = models.TextField(max_length=255, null=False, blank=False, default='')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timeStamp = models.DateTimeField(default=get_time)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)


class Attendance(models.Model):
    ATTENDANCE_TYPE = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_type = models.CharField(max_length=255, default='Present', choices=ATTENDANCE_TYPE, null=True,
                                       blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    attendance_date = models.DateField(null=False, blank=False, default=datetime.date.today)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)