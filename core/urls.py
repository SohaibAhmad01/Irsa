from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from . import views
from programmodule.views import *
from classmodule.views import *
from librarymodule.views import *
from studentmodule.views import *
from teachermodule.views import *
from adminmodule.views import *

router = DefaultRouter(trailing_slash=False)

router.register(r'programs', ProgramView)
router.register(r'courses', CourseView)
router.register(r'course_content', CourseContentView)
router.register(r'irsa_classes', ClassView)
router.register(r'students/adr', StudentView)
router.register(r'news', views.NewsSection)
router.register(r'library', LibraryView)
router.register(r'publication', PublicationView)
router.register(r'resource', ResourcesView)

urlpatterns = [

    path('auth/logout', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('admin_auth/refresh', views.RefreshView.as_view(), name='admin_token_refresh'),
    path('teacher_auth/refresh', views.RefreshView.as_view(), name='teacher_token_refresh'),
    path('student_auth/refresh', views.RefreshView.as_view(), name='student_token_refresh'),
    path('teachers/p/faculty', TeacherList.as_view(), name='teacher_list'),
    path('programs/p/getall/', ProgramList.as_view(), name='program_list'),
    path('library/p/getall/', LibraryList.as_view(), name='library_list'),
    path('publication/p/getall/', PublicationList.as_view(), name='publication_list'),
    path('resources/p/getall/', ResourcesList.as_view(), name='resource_list'),

    path("news/p/getall/", views.NewsList.as_view({
        "get": "list",
    })),
    path("news/p/getall/<int:pk>", views.NewsList.as_view({
        "get": "retrieve",
    })),

    ##   admin section urls
    path("admin_auth/register", AdminUserView.as_view({
        "post": "create",
    })),
    path("admin_auth/getadmins", AdminUserView.as_view({
        "get": "list",
    })),
    path("admin_auth/me", AdminUserView.as_view({
        "get": "get_own_profile",
    })),
    path("admin_auth/profile/<int:pk>", AdminUserView.as_view({
        "get": "get_admin_profile",
    })),
    path("admin_auth/profile/edit/<int:pk>", AdminUserView.as_view({
        "put": "update",
    })),
    path("admin_auth/profile/delete/<int:pk>", AdminUserView.as_view({
        "delete": "destroy",
    })),
    path("admin/stats", AdminUserView.as_view({
        "get": "get_admin_stats",
    })),
    path("auth/login", views.Login.as_view({
        "post": "create",
    })),
    path("auth/forgotpassword", views.ForgotResetPasswordView.as_view({
        "post": "forgot_password",
    })),
    path("auth/resetpassword", views.ForgotResetPasswordView.as_view({
        "post": "reset_password",
    })),

    ##   student section urls
    path("std_auth/register", StudentView.as_view({
        "post": "create",
    })),
    path("std_auth/profile/edit/<int:pk>", StudentView.as_view({
        "put": "update",
    })),
    path("student_auth/me", StudentView.as_view({
        "get": "get_own_profile",
    })),
    path("std_auth/profile/<int:pk>", StudentView.as_view({
        "get": "get_student_profile",
    })),
    path("student/stats", StudentView.as_view({
        "get": "get_student_stats",
    })),

    ##   teacher section urls
    path("tchr_auth/profile/<int:pk>", TeacherView.as_view({
        "get": "get_teacher_profile",
    })),
    path("tchr_auth/profile/edit/<int:pk>", TeacherView.as_view({
        "put": "update",
    })),
    path("tchr_auth/forgotpassword", views.ForgotResetPasswordView.as_view({
        "post": "forgot_password",
    })),
    path("tchr_auth/register", TeacherView.as_view({
        "post": "create",
    })),
    path("teacher_auth/me", TeacherView.as_view({
        "get": "get_own_profile",
    })),
    path("tchr_auth/updatepassword", TeacherView.as_view({
        "put": "update_password",
    })),
    path("teachers/adr/<int:pk>", TeacherView.as_view({
        "delete": "destroy",
    })),
    path("teachers/adr", TeacherView.as_view({
        "get": "list",
    })),
    path("teacher/stats", TeacherView.as_view({
        "get": "get_teacher_stats",
    })),

    path("course_content/tchr/create", CourseContentView.as_view({
        "post": "create",
    })),

    path("course_content/getbycourseid/<int:pk>", CourseContentView.as_view({
        "get": "get_content_by_course",
    })),

    # class section
    path("irsa_classes/changestatus/<int:pk>", ClassView.as_view({
        "post": "change_class_status",
    })),
    path("irsa_classes/getclass/<int:pk>", ClassView.as_view({
        "get": "get_class_all_details",
    })),

    path("irsa_classes/getstudentstoenroll/<int:pk>", ClassView.as_view({
        "get": "get_all_students_enroll",
    })),
    path("irsa_classes/enrollstudents/<int:pk>", ClassView.as_view({
        "post": "add_student_in_class",
    })),
    path("irsa_classes/removestudent", ClassView.as_view({
        "post": "remove_student_from_class",
    })),
    path("programs/p/stats", views.StatsView.as_view({
        "get": "list",
    })),

    #### Messages urls
    path("chat/<int:pk>", MessageView.as_view({
        "post": "create",
    })),
    path("classchat/<int:pk>", MessageView.as_view({
        "get": "list",
    })),
    path("alluserchat/", MessageView.as_view({
        "get": "userAllChats",
    })),
    path("attendance/<int:pk>", AttendanceView.as_view({
        "post": "create",
    })),
    path("studentinclass/<int:pk>", AttendanceView.as_view({
        "get": "get_students_in_class",
    })),
    path("attendance/stats/<int:pk>", AttendanceView.as_view({
        "get": "get_stats_attendance",
    })),
    path("attendance/edit/<int:pk>", AttendanceView.as_view({
        "put": "update",
    })),
    path("classdetails/<int:pk>", MessageView.as_view({
        "get": "classDetails",
    })),

]

urlpatterns += router.urls
