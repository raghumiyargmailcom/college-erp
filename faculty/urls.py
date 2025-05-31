from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
   path('dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
   path('manage_students/', views.manage_students, name='manage_students'),
path('update_student/', views.update_student, name='update_student'),
path('delete_student/<str:rollno>/', views.delete_student, name='delete_student'),
    path('my_leave_status/', views.faculty_leave_status, name='my_leave_status'),
    path('exam_schedule/', views.faculty_exam_schedule, name='exam_schedule'),
     path('faculty-leave/', views.apply_leave, name='faculty_leave'),
     path('leave-status/', views.faculty_leave_status, name='faculty_leave_status'),
     path('take_attendance/', views.take_attendance, name='take_attendance'),
    path('attendance_report/', views.attendance_report, name='attendance_report'),
]
