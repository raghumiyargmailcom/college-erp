from django.contrib import admin
from .models import Childrens, Faculty, HOD,Marks

@admin.register(Childrens)
class ChildrensAdmin(admin.ModelAdmin):
    list_display = ('rollno', 'name', 'email', 'class_name')
    search_fields = ('rollno', 'name', 'email', 'class_name')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'name', 'email', 'department')
    search_fields = ('faculty_id', 'name', 'email', 'department')

@admin.register(HOD)
class HODAdmin(admin.ModelAdmin):
    list_display = ('hod_id', 'name', 'email', 'department')
    search_fields = ('hod_id', 'name', 'email', 'department')



@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester', 'marks_obtained', 'total_marks', 'max_marks')
    list_filter = ('semester', 'subject')
    search_fields = ('student__name', 'subject__name')

    from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'status', 'date')
    list_filter = ('status', 'date', 'subject')
    search_fields = ('student__name', 'subject__name')

admin.site.register(Attendance, AttendanceAdmin)

