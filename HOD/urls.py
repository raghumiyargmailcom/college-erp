from django.urls import path
from . import views  # Import all views

app_name = 'hod'  # Namespace for HOD URLs

urlpatterns = [
   


    path('dashboard/', views.hod_dashboard, name='hod_dashboard'),  # HOD Dashboard
   path('manage_students/', views.manage_students, name='manage_students'),
    path('update_student/', views.update_student, name='update_student'),
    path('delete_student/<str:rollno>/', views.delete_student, name='delete_student'),

    # Faculty Management
    path('manage_faculty/', views.manage_faculty, name='manage_faculty'),
   path("update_faculty/", views.update_faculty, name="update_faculty"),
    path("delete_faculty/<int:faculty_id>/", views.delete_faculty, name="delete_faculty"),
    # Timetable Management
    

    # ✅ Leave Management for Students
    path('student-leave/', views.manage_student_leave_requests, name='manage_student_leave_requests'),
path('student-leave/approve/<int:leave_id>/', views.approve_student_leave, name='approve_student_leave'),
path('student-leave/reject/<int:leave_id>/', views.reject_student_leave, name='reject_student_leave'),


    path("add_marks/", views.add_marks, name="add_marks"),  # ✅ Add this line

#✅ Leave Management for Students
    
    path('manage-student-marks/', views.manage_student_marks, name='manage_student_marks'),
    
    path('delete-student-marks/', views.delete_student_marks, name='delete_student_marks'),

    path('manage_faculty_leave_requests/', views.manage_leave_requests, name='manage_faculty_leave_requests'),
    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    
]





    

