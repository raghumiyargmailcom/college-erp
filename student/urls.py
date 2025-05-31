from django.urls import path
from . import views

app_name = "student"  # ✅ Ensure namespace is set correctly

urlpatterns = [
   
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('exam-schedule/', views.exam_schedule, name='exam_schedule'),
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('profile/', views.update_profile, name='profile'),
  # ✅ Renamed from update_profile → profile
    path('my-marks/', views.view_my_marks, name='view_my_marks'),
    path('my-marks/download/', views.download_my_marks_pdf, name='download_my_marks'),
    path('my-leave-status/', views.my_leave_status, name='my_leave_status'),
    path('student_attendance_report/', views.student_attendance_report, name='student_attendance_report'),
]


