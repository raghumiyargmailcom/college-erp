from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from controll.models import Childrens, ExamSchedule, LeaveApplication, HOD
from django.db import IntegrityError
from .forms import ProfileUpdateForm

def student_dashboard(request):
    """Student Dashboard View"""
    if "student_rollno" not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("student_login")  # ✅ Redirects correctly

    student_rollno = request.session.get("student_rollno")
    student_email = request.session.get("student_email")

    print(f"✅ Student Dashboard Loaded: Roll No - {student_rollno}, Email - {student_email}")  # Debugging

    return render(request, "student_dashboard.html", {"student_rollno": student_rollno, "student_email": student_email})


def exam_schedule(request):
    """Student View for Exam Schedule"""

    if "student_rollno" not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("student_login")  

    exams = ExamSchedule.objects.all().order_by("exam_date", "start_time")

    print("📌 Exam Schedule Loaded:", exams)  # Debugging

    return render(request, "exam_schedule.html", {"exams": exams})


#apply leave


import traceback
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from controll.models import Childrens, HOD, LeaveApplication

def apply_leave(request):
    if "student_rollno" not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("student_login")

    student_rollno = request.session.get("student_rollno")

    try:
        student = Childrens.objects.get(rollno=student_rollno)
    except Childrens.DoesNotExist:
        messages.error(request, "Student record not found.")
        return redirect("student_login")

    hod = HOD.objects.filter(department=student.department).first()

    if request.method == "POST":
        reason = request.POST.get("reason")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Basic validation
        if not reason or not start_date_str or not end_date_str:
            messages.error(request, "All fields are required.")
            return redirect("student:apply_leave")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()

            # Server-side date validation
            if start_date < today:
                messages.error(request, "Start date cannot be in the past.")
                return redirect("student:apply_leave")

            if end_date <= start_date:
                messages.error(request, "End date must be after start date.")
                return redirect("student:apply_leave")

            if hod:
                leave_request = LeaveApplication.objects.create(
                    student=student,
                    hod=hod,
                    reason=reason,
                    date_from=start_date,
                    date_to=end_date,
                    status="Pending"
                )
                messages.success(request, "Leave request submitted.")
                return redirect("student:student_dashboard")
            else:
                messages.error(request, "No HOD found for your department.")
                return redirect("student:apply_leave")

        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("student:apply_leave")

        except Exception as e:
            print("❌ Error:", e)
            traceback.print_exc()
            messages.error(request, "An error occurred. Please try again.")
            return redirect("student:apply_leave")

    return render(request, "apply_leave.html", {"student": student})


#profile


def update_profile(request):
    student_email = request.session.get("student_email")  # ✅ Get email from session
    print(f"🔍 Session student_email: {student_email}")  # Debugging

    if not student_email:
        messages.error(request, "Student not found. Please log in again.")
        return redirect("student_login")  # ✅ Redirects to student login if session is missing

    try:
        student = Childrens.objects.get(email=student_email)  # ✅ Get student by email
    except Childrens.DoesNotExist:
        print("❌ No matching student found in the database!")  # Debugging
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect("student_dashboard")  # ✅ Redirects to student dashboard

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("student:profile")  # ✅ Correct URL with namespace
    else:
        form = ProfileUpdateForm(instance=student)

    return render(request, "profile.html", {"form": form, "student": student})  # ✅ Ensure `profile.html` exists


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from controll.models import Childrens, Marks, Subject


def view_my_marks(request):
    if not request.session.get('student_email'):
        return render(request, 'student/unauthorized.html')

    student = get_object_or_404(Childrens, email=request.session['student_email'])
    subjects = Subject.objects.filter(department=student.department)
    marks = Marks.objects.filter(student=student, subject__in=subjects)

    marks_dict = {mark.subject.name: mark.marks_obtained for mark in marks}
    total = sum(marks_dict.values())
    average = round((total / (len(subjects) * 50)) * 100, 2) if subjects else 0

    context = {
        'student': student,
        'marks_dict': marks_dict,
        'total': total,
        'average': average,
    }
    return render(request, 'view_my_marks.html', context)


def download_my_marks_pdf(request):
    if not request.session.get('student_email'):
        return render(request, 'student/unauthorized.html')

    student = get_object_or_404(Childrens, email=request.session['student_email'])
    subjects = Subject.objects.filter(department=student.department)
    marks = Marks.objects.filter(student=student, subject__in=subjects)

    marks_dict = {mark.subject.name: mark.marks_obtained for mark in marks}
    total = sum(marks_dict.values())
    average = round((total / (len(subjects) * 50)) * 100, 2) if subjects else 0

    context = {
        'student': student,
        'marks_dict': marks_dict,
        'total': total,
        'average': average,
    }

    template_path = 'view_my_marks.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="My_Marks.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response


from django.shortcuts import render, get_object_or_404
from controll.models import Childrens, LeaveApplication

def my_leave_status(request):
    if not request.session.get('student_email'):
        return render(request, 'student/unauthorized.html')

    student = get_object_or_404(Childrens, email=request.session['student_email'])
    leaves = LeaveApplication.objects.filter(student=student).order_by('-date_from')  # ✅ Correct field

    context = {
        'student': student,
        'leaves': leaves,
    }
    return render(request, 'my_leave_status.html', context)


from django.shortcuts import render
from django.http import HttpResponse
from controll.models import Attendance, Childrens
from django.template.loader import get_template
import matplotlib.pyplot as plt
import os
from io import BytesIO
from xhtml2pdf import pisa
import base64
from collections import defaultdict

def student_attendance_report(request):
    student_email = request.session.get('student_email')
    if not student_email:
        return HttpResponse("Student not logged in.", status=401)

    try:
        student = Childrens.objects.get(email=student_email)
    except Childrens.DoesNotExist:
        return HttpResponse("Student not found.", status=404)

    attendance_records = Attendance.objects.filter(student=student).select_related('subject')

    # Subject-wise breakdown
    subject_data = defaultdict(lambda: {'present': 0, 'absent': 0})
    total_present = total_absent = 0

    for record in attendance_records:
        subject = record.subject.name
        if record.status == 'P':
            subject_data[subject]['present'] += 1
            total_present += 1
        elif record.status == 'A':
            subject_data[subject]['absent'] += 1
            total_absent += 1

    total_classes = total_present + total_absent

    # Generate combined pie chart
    pie_chart_base64 = None
    if total_classes > 0:
        labels = ['Present', 'Absent']
        sizes = [total_present, total_absent]
        colors = ['#2ecc71', '#e74c3c']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        pie_chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close(fig)

    context = {
        'student': student,
        'subject_data': dict(subject_data),
        'total_present': total_present,
        'total_absent': total_absent,
        'total_classes': total_classes,
        'pie_chart': pie_chart_base64,
        'download': 'download' in request.GET,
    }

    if 'download' in request.GET:
        template = get_template('student_attendance_report.html')
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response

    return render(request, 'student_attendance_report.html', context)
