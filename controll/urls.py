from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import subject_list, add_subject, update_subject, delete_subject

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Corrected line
    path('admin_home/', views.admin_home, name='admin_home'),

    # Student Management

    path('import_students/', views.import_students, name='import_students'),
    path('manage_student/', views.manage_students, name='manage_student'),
    path('update_student/', views.update_student, name='update_student'),  # ✅ Removed <str:rollno>
    path('delete_student/', views.delete_student, name='delete_student'),  # ✅ Removed <str:rollno>

    # Faculty Management
    path('import_faculty/', views.import_faculty, name='import_faculty'),
    path('manage_faculty/', views.manage_faculty, name='manage_faculty'),
    path("update_faculty/", views.update_faculty, name="update_faculty"),  # Ensure views.update_faculty is used
    path('delete_faculty/<str:faculty_id>/', views.delete_faculty, name='delete_faculty'),

    # HOD Management
    path('add_hod/', views.add_hod, name='add_hod'),
    path('manage_hod/', views.manage_hod, name='manage_hod'),
   path('update_hod/<int:hod_id>/', views.update_hod, name='update_hod'),
    path('delete_hod/<str:hod_id>/', views.delete_hod, name='delete_hod'),

    # Principal Management
    path('add_principle/', views.add_principal, name='add_principle'),
path('manage_principle/', views.manage_principal, name='manage_principle'),
path('delete_principal/<int:principal_id>/', views.delete_principal, name='delete_principal'),
path('update_principal/<int:principal_id>/', views.update_principal, name='update_principal'),


    # Exam Schedule Management
    path('schedule-exam/', views.schedule_exam, name='schedule_exam'),
    path('manage-exam-schedule/', views.manage_exam_schedule, name='manage_exam_schedule'),
    path('update-exam/<int:exam_id>/', views.update_exam, name='update_exam'),
    path('delete-exam/<int:exam_id>/', views.delete_exam, name='delete_exam'),

    # Student Login Page
    path('student_login/', views.student_login, name='student_login'),

    path('subjects/', subject_list, name='subject_list'),  # ✅ Subject List
    path('add-subject/', add_subject, name='add_subject'),
    path('update-subject/<int:subject_id>/', update_subject, name='update_subject'),
    path('delete-subject/<int:subject_id>/', delete_subject, name='delete_subject'),
]
