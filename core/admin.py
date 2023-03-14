from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, OtpTemp
from adminmodule.models import AdminUser
from classmodule.models import Class, Attendance
from programmodule.models import *
from studentmodule.models import *
from teachermodule.models import *
from librarymodule.models import *


# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(OtpTemp)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(CourseContent)
admin.site.register(Class)
admin.site.register(Programs)
admin.site.register(Library)
admin.site.register(AdminUser)
admin.site.register(Resources)
admin.site.register(Attendance)
admin.site.register(Publication)
