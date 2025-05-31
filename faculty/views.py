from django.shortcuts import render, redirect
from controll.models import Faculty  # Assuming the Faculty model is in the 'controll' app

def faculty_dashboard(request):
    # ✅ Check if faculty is logged in via session
    faculty_email = request.session.get('faculty_email')

    if not faculty_email:
        return redirect('student_login')  # 🔁 Redirect to faculty login if no session

    try:
        faculty = Faculty.objects.get(email=faculty_email)
    except Faculty.DoesNotExist:
        return redirect('student_login')  # 🔁 Redirect if email is invalid

    # Pass the faculty details to the template context
    context = {
        'faculty_email': faculty.email,
        'faculty_name': faculty.name,
        'faculty_department': faculty.department,
    }

    # Render the dashboard template with the context
    return render(request, 'faculty_dashboard.html', context)


#manage students
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from controll.models import Faculty, Childrens

def manage_students(request):
    if "faculty_email" not in request.session:
        return redirect('controll:student_login')

    try:
        faculty = Faculty.objects.get(email=request.session["faculty_email"])
        students = Childrens.objects.filter(department=faculty.department)
    except Faculty.DoesNotExist:
        return redirect('controll:student_login')

    return render(request, 'manage_students.html', {'students': students})


@csrf_exempt  # Needed to avoid redirect on CSRF fail via AJAX
@require_POST
def update_student(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    rollno = request.POST.get('rollno')
    name = request.POST.get('name')
    email = request.POST.get('email')
    class_name = request.POST.get('class_name')
    department = request.POST.get('department')
    phone = request.POST.get('phone_number')
    address = request.POST.get('address')

    faculty_email = request.session.get('faculty_email')
    try:
        faculty = Faculty.objects.get(email=faculty_email)
        student = Childrens.objects.get(rollno=rollno, department=faculty.department)

        student.name = name
        student.email = email
        student.class_name = class_name
        student.department = department
        student.phone_number = phone
        student.address = address
        student.save()

        return JsonResponse({'status': 'success', 'message': 'Student updated successfully.'})
    except (Childrens.DoesNotExist, Faculty.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Student not found or unauthorized.'})

    return JsonResponse({'status': 'success', 'message': 'Student updated successfully'})


def delete_student(request, rollno):
    if "faculty_email" not in request.session or request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Unauthorized or invalid request'}, status=403)

    student = get_object_or_404(Childrens, rollno=rollno)
    student.delete()

    return JsonResponse({'status': 'success', 'message': 'Student deleted successfully'})




# faculty/views.py
# faculty/views.py
from django.shortcuts import render, get_object_or_404
from controll.models import Faculty, LeaveApplication, Childrens

def faculty_leave_status(request):
    if not request.session.get('faculty_email'):
        return render(request, 'faculty/unauthorized.html')  # Unauthorized page if the faculty is not logged in

    # Get the faculty object from the session
    faculty = get_object_or_404(Faculty, email=request.session['faculty_email'])

    # Get students in the same department as the logged-in faculty
    students_in_dept = Childrens.objects.filter(department=faculty.department)

    # Fetch leave requests for those students
    leaves = LeaveApplication.objects.filter(student__in=students_in_dept).order_by('-date_from')

    context = {
        'faculty': faculty,
        'leaves': leaves,
    }

    return render(request, 'my_leave_status.html', context)

#exam schedule
# faculty/views.py
from django.shortcuts import render
from controll.models import ExamSchedule  # Assuming ExamSchedule model is defined in the controll app

def faculty_exam_schedule(request):
    """Faculty View for Exam Schedule"""

    if "faculty_email" not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("student_login")  # Redirect to login if session is expired

    exams = ExamSchedule.objects.all().order_by("exam_date", "start_time")

    print("📌 Exam Schedule Loaded:", exams)  # Debugging

    return render(request, "exam_schedule.html", {"exams": exams})



import traceback  # ✅ For detailed error tracking
from django.shortcuts import render, redirect
from django.contrib import messages
from controll.models import FacultyLeaveApplication, Faculty, HOD  # Ensure proper import of models

from datetime import datetime, date
from django.shortcuts import render, redirect
from django.contrib import messages
import traceback
from controll.models import Faculty, HOD, FacultyLeaveApplication

def apply_leave(request):
    """Faculty applies for leave and notifies the HOD."""

    if "faculty_email" not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("student_login")

    faculty_email = request.session.get("faculty_email")

    try:
        faculty = Faculty.objects.get(email=faculty_email)
        print(f"✅ Faculty Found: {faculty.name} ({faculty.email})")
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty record not found.")
        return redirect("student_login")

    hod = HOD.objects.filter(department=faculty.department).first()

    if request.method == "POST":
        reason = request.POST.get("reason")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        if not reason or not start_date_str or not end_date_str:
            messages.error(request, "All fields are required.")
            return redirect("faculty:faculty_leave")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            today = date.today()

            # Validation 1: Start date should be in the future
            if start_date < today:
                messages.error(request, "Start date must be a future date.")
                return redirect("faculty:faculty_leave")

            # Validation 2: End date should be after start date
            if end_date < start_date:
                messages.error(request, "End date must be after start date.")
                return redirect("faculty:faculty_leave")

            if hod:
                leave_request = FacultyLeaveApplication.objects.create(
                    faculty=faculty,
                    hod=hod,
                    reason=reason,
                    date_from=start_date,
                    date_to=end_date,
                    status="Pending"
                )
                print(f"✅ Leave Saved: {leave_request}")
                messages.success(request, "Leave request submitted.")
                return redirect("faculty:faculty_dashboard")

            else:
                messages.error(request, "No HOD found for your department.")
                return redirect("faculty:faculty_leave")

        except ValueError:
            messages.error(request, "Invalid date format. Please use the date picker.")
            return redirect("faculty:faculty_leave")

        except Exception as e:
            print(f"❌ Error Saving Leave: {e}")
            traceback.print_exc()
            messages.error(request, "Error saving leave request. Try again.")
            return redirect("faculty:faculty_leave")

    return render(request, "faculty_leave.html", {
        "faculty": faculty,
        "today": date.today().isoformat()  # Pass to template for min date
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from controll.models import FacultyLeaveApplication, Faculty, HOD  # Assuming Faculty and HOD models exist

# Check if HOD is authenticated and belongs to the correct department
def is_hod_authenticated(request):
    """Check if HOD is logged in and exists in DB."""
    if 'hod_email' in request.session:
        return HOD.objects.filter(email=request.session['hod_email']).exists()
    return False

# views.py (for HOD)
# HOD/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from controll.models import Faculty, FacultyLeaveApplication

def faculty_leave_status(request):
    if 'faculty_email' not in request.session:
        messages.error(request, "Please login as Faculty.")
        return redirect('controll:student_login')  # Make sure this URL is registered

    # Get the logged-in faculty
    faculty = get_object_or_404(Faculty, email=request.session['faculty_email'])

    # Get only this faculty's leave records
    leave_records = FacultyLeaveApplication.objects.filter(
        faculty=faculty
    ).order_by('-date_from')

    context = {
        'leave_records': leave_records
    }
    return render(request, "faculty_leave_status.html", context)




from django.shortcuts import render, redirect
from django.contrib import messages
from controll.models import Childrens, Subject, Attendance

def take_attendance(request):
    classes = ['1 MCA', '2 MCA']
    students = []
    subjects = []
    selected_class = request.GET.get('class_name')
    selected_semester = request.GET.get('semester')

    faculty_department = request.session.get('faculty_department')
    print("🔍 Selected class:", selected_class)
    print("🔍 Selected semester:", selected_semester)
    print("✅ Faculty department from session:", faculty_department)

    if selected_class:
        students = list(Childrens.objects.filter(class_name=selected_class))

    if selected_semester and faculty_department:
        subjects = list(Subject.objects.filter(department=faculty_department, semester=selected_semester))

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        semester = request.POST.get('semester')
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')

        try:
            students = Childrens.objects.filter(class_name=class_name)
            for student in students:
                status = request.POST.get(f'status_{student.rollno}')
                if status:
                    Attendance.objects.create(
                        student=student,
                        subject_id=subject_id,
                        status=status,
                        date=date
                    )
            messages.success(request, "✅ Attendance recorded successfully!")
        except Exception as e:
            print("❌ Error saving attendance:", e)
            messages.error(request, "❌ Failed to record attendance.")
        return redirect('faculty:take_attendance')

    return render(request, 'take_attendance.html', {
        'classes': classes,
        'students': students,
        'selected_class': selected_class,
        'selected_semester': selected_semester,
        'subjects': subjects,
    })

from django.shortcuts import render
from controll.models import Attendance

def attendance_report(request):
    attendance_records = Attendance.objects.select_related('student', 'subject').order_by('-date')

    return render(request, 'attendance_report.html', {
        'attendance_records': attendance_records
    })
