from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Correct import
from django.http import JsonResponse,HttpResponseNotAllowed
from controll.models import HOD, Childrens, Faculty,LeaveApplication ,Marks   # Import LeaveRequest model
  # Ensure forms are correctly imported
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token





def hod_dashboard(request):
    """Render the HOD dashboard if logged in."""
    if request.session.get("hod_id"):  # ✅ Check `hod_id` in session
        return render(request, "HOD/hod_dashboard.html")
    else:
        messages.error(request, "Please log in first.")
        return redirect("student_login")  # Redirects to common login page

def hod_logout(request):
    """Log out the HOD by clearing session data."""
    if 'hod_id' in request.session:
        request.session.flush()  # ✅ Clears all session data
        messages.success(request, "You have been logged out.")
    
    return redirect('student_login')  # ✅ Redirect to login page
#MANAGE STUDENT




def manage_students(request):
    print("🔹 Checking Authentication in manage_students view")

    # ✅ Manually check if session is set
    if "hod_email" not in request.session:
        print("🚨 User is NOT authenticated! Redirecting to login...")
        return redirect('student_login')

    try:
        # ✅ Get the logged-in HOD using the session email
        hod = HOD.objects.get(email=request.session["hod_email"])
        hod_department = hod.department
        print(f"✅ HOD Found: {hod}, Department: {hod_department}")
    except HOD.DoesNotExist:
        print("❌ HOD Not Found! Redirecting to login.")
        return redirect('student_login')

    # ✅ Filter students based on the HOD's department
    students = Childrens.objects.filter(department=hod_department)
    print(f"✅ Found {students.count()} students for department {hod_department}")

    return render(request, 'HOD/manage_students.html', {'students': students})

from django.views.decorators.http import require_POST
csrf_exempt
def update_student(request):
    print("🔄 Update Student View Called")

    # ✅ DO NOT use request.user or session if you want this public
    if request.method == 'POST':
        rollno = request.POST.get('rollno')
        name = request.POST.get('name')
        email = request.POST.get('email')
        class_name = request.POST.get('class_name')
        department = request.POST.get('department')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        try:
            student = Childrens.objects.get(rollno=rollno)
            student.name = name
            student.email = email
            student.class_name = class_name
            student.department = department
            student.phone_number = phone_number
            student.address = address
            student.save()
            print(f"✅ Student {rollno} updated successfully.")
            return JsonResponse({'success': True})
        except Childrens.DoesNotExist:
            print(f"❌ Student with rollno {rollno} not found.")
            return JsonResponse({'success': False, 'error': 'Student not found'})

    print("❌ Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def delete_student(request, rollno):
    if request.method == 'DELETE':
        student = get_object_or_404(Childrens, rollno=rollno)
        student.delete()
        return JsonResponse({"status": "deleted"})

    return HttpResponseNotAllowed(['DELETE'])
# manage faculty
def manage_faculty(request):
    print("🔹 Checking Authentication in manage_faculty view")

    # ✅ Check if session is set
    if "hod_email" not in request.session:
        print("🚨 User is NOT authenticated! Redirecting to login...")
        return redirect('student_login')  # Ensure this is the correct login URL for HOD

    try:
        # ✅ Get the logged-in HOD using the session email
        hod = HOD.objects.get(email=request.session["hod_email"])
        hod_department = hod.department
        print(f"✅ HOD Found: {hod}, Department: {hod_department}")
    except HOD.DoesNotExist:
        print("❌ HOD Not Found! Redirecting to login.")
        return redirect('student_login')

    # ✅ Debug: Print Faculty Data
    faculty_members = Faculty.objects.filter(department=hod_department)
    print(f"✅ Found {faculty_members.count()} faculty members for department: {hod_department}")

    for faculty in faculty_members:
        print(f"👤 Faculty: {faculty.name}, Department: {faculty.department}")

    return render(request, 'HOD/manage_faculty.html', {'faculty_members': faculty_members})



# update faculty

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from controll.models import Faculty

@csrf_exempt
def update_faculty(request):
    if request.method == "POST":
        faculty_id = request.POST.get("faculty_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        department = request.POST.get("department")
        password = request.POST.get("password")

        try:
            faculty = get_object_or_404(Faculty, faculty_id=faculty_id)  # Use faculty_id not id
            faculty.name = name
            faculty.email = email
            faculty.department = department
            if password:
                faculty.password = password  # Password will be hashed in model's save()
            faculty.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def delete_faculty(request, faculty_id):
    try:
        faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
        faculty.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})





#aprove leave

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from controll.models import LeaveApplication, HOD, Childrens  # Use your actual models

def manage_student_leave_requests(request):
    if 'hod_email' not in request.session:
        return redirect('controll:student_login')  # Adjust redirect if needed

    hod = get_object_or_404(HOD, email=request.session['hod_email'])

    # Filter leave applications for students in this HOD's department
    leave_requests = LeaveApplication.objects.filter(
        student__department=hod.department
    ).select_related('student')

    return render(request, 'HOD/manage_student_leave_requests.html', {
    'leave_requests': leave_requests,
})


def approve_student_leave(request, leave_id):
    leave = get_object_or_404(LeaveApplication, id=leave_id)
    leave.status = 'Approved'
    leave.save()
    messages.success(request, "Leave approved.")
    return redirect('HOD:manage_student_leave_requests')

def reject_student_leave(request, leave_id):
    leave = get_object_or_404(LeaveApplication, id=leave_id)
    leave.status = 'Rejected'
    leave.save()
    messages.error(request, "Leave rejected.")
    return redirect('HOD:manage_student_leave_requests')

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from controll.models import Childrens, Subject, Marks

@csrf_exempt
@login_required
def add_marks(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # AJAX request for subject loading
            roll_number = request.POST.get('roll_number')
            semester = request.POST.get('semester')

            try:
                student = Childrens.objects.get(rollno=roll_number)
                subjects = Subject.objects.filter(semester=semester, department=student.department)
                subject_data = [{'id': sub.id, 'name': sub.name} for sub in subjects]
                return JsonResponse(subject_data, safe=False)
            except Childrens.DoesNotExist:
                return JsonResponse([], safe=False)

        # Handling form submission
        roll_number = request.POST.get('roll_number')
        semester = request.POST.get('semester')
        max_marks = 50  # Always 50

        try:
            student = Childrens.objects.get(rollno=roll_number)
            subjects = Subject.objects.filter(semester=semester, department=student.department)
        except Childrens.DoesNotExist:
            messages.error(request, "Student not found.")
            return redirect('HOD:add_marks')

        errors = []

        for subject in subjects:
            key = f'marks_{subject.id}'
            mark_str = request.POST.get(key)
            if mark_str is None:
                errors.append(f"Marks for {subject.name} not provided.")
                continue

            try:
                mark = int(mark_str)
                if mark < 0 or mark > max_marks:
                    errors.append(f"{subject.name}: Marks must be between 0 and {max_marks}.")
            except ValueError:
                errors.append(f"{subject.name}: Invalid number.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('HOD:add_marks')

        # Save marks if all are valid
        for subject in subjects:
            mark = int(request.POST.get(f'marks_{subject.id}'))
            Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={'marks': mark, 'max_marks': max_marks}
            )

        messages.success(request, "Marks submitted successfully.")
        return redirect('HOD:add_marks')

    return render(request, 'HOD/add_marks.html')

        # ✅ Process max marks
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from controll.models import Marks, Subject, Childrens, HOD  

def add_marks(request):
    rollno = None
    subjects = []
    student = None

    if request.method == "POST":
        rollno = request.POST.get("roll_number", "").strip()
        semester = request.POST.get("semester")

        if not rollno:
            messages.error(request, "Enter Roll Number properly.")
            return redirect("HOD:add_marks")

        # ✅ Get the logged-in HOD using the session-stored HOD ID
        hod_id = request.session.get("hod_id")  
        if not hod_id:
            messages.error(request, "HOD session not found. Please log in again.")
            return redirect("login")  # Redirect to login page

        try:
            hod = HOD.objects.get(hod_id=hod_id)  # ✅ Fetch HOD using `hod_id`
        except HOD.DoesNotExist:
            messages.error(request, "HOD not found in the database.")
            return redirect("HOD:add_marks")

        try:
            student = Childrens.objects.get(rollno=rollno)
        except Childrens.DoesNotExist:
            messages.error(request, "No student found with this Roll Number.")
            return redirect("HOD:add_marks")

        # ✅ Fetch only subjects of the HOD's department
        subjects = Subject.objects.filter(semester=semester, department=hod.department)

        if not subjects.exists():
            messages.error(request, "No subjects found for this semester in your department.")
            return redirect("HOD:add_marks")

        # ✅ AJAX Request for Subjects
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            subject_list = [{"id": sub.id, "name": sub.name} for sub in subjects]
            return JsonResponse(subject_list, safe=False)

        # ✅ If marks are being submitted
        if "submit_marks" in request.POST:
            total_marks = 0
            max_marks = int(request.POST.get("max_marks", 100))

            for subject in subjects:
                marks_obtained = request.POST.get(f"marks_{subject.id}", "0")

                try:
                    marks_obtained = int(marks_obtained)
                    if marks_obtained > max_marks:
                        messages.error(request, f"Marks for {subject.name} cannot exceed {max_marks}.")
                        return redirect("HOD:add_marks")

                    total_marks += marks_obtained

                    mark_entry, created = Marks.objects.get_or_create(
                        student=student,
                        subject=subject,
                        semester=semester,
                        defaults={"marks_obtained": marks_obtained, "max_marks": max_marks},
                    )

                    if not created:
                        mark_entry.marks_obtained = marks_obtained
                        mark_entry.save()

                except ValueError:
                    messages.error(request, "Invalid marks format.")
                    return redirect("HOD:add_marks")

            messages.success(request, "Marks added successfully!")
            return redirect("HOD:add_marks")

    return render(
        request,
        "HOD/add_marks.html",
        {"subjects": subjects, "student": student, "rollno": rollno},
    )

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from controll.models import Childrens, Subject, Marks, HOD

# View to manage student marks
def manage_student_marks(request):
    if not request.session.get('hod_email'):
        return HttpResponseForbidden("Unauthorized Access")

    hod = get_object_or_404(HOD, email=request.session['hod_email'])
    subjects = Subject.objects.filter(department=hod.department)
    students = Childrens.objects.filter(department=hod.department)

    student_data = []
    for student in students:
        marks_list = []
        total = 0
        for subject in subjects:
            mark_obj = Marks.objects.filter(student=student, subject=subject).first()
            if mark_obj:
                marks_list.append(mark_obj.marks_obtained)
                total += mark_obj.marks_obtained
            else:
                marks_list.append(0)
        average = round((total / (len(subjects) * 50)) * 100, 2) if subjects else 0

        student_data.append({
            'student': student,
            'marks_list': marks_list,
            'total': total,
            'average': average
        })

    return render(request, 'HOD/manage_student_marks.html', {
        'subjects': subjects,
        'student_data': student_data,
    })

# Delete all marks for a student
@csrf_exempt
def delete_student_marks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    if not request.session.get('hod_email'):
        return JsonResponse({'success': False, 'error': 'Unauthorized Access'})

    hod = get_object_or_404(HOD, email=request.session['hod_email'])
    student_rollno = request.POST.get('student_id')
    student = get_object_or_404(Childrens, rollno=student_rollno)

    if student.department != hod.department:
        return JsonResponse({'success': False, 'error': 'Access denied.'})

    try:
        Marks.objects.filter(student=student).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from controll.models import FacultyLeaveApplication, Faculty, HOD  # Ensure these models exist

# Check if HOD is authenticated and belongs to the correct department
def is_hod_authenticated(request):
    """Check if HOD is logged in and exists in DB."""
    if 'hod_email' in request.session:
        return HOD.objects.filter(email=request.session['hod_email']).exists()
    return False

# HOD managing leave requests of faculty in their department
def manage_leave_requests(request):
    if 'hod_email' not in request.session:
        return redirect('controll:student_login')

    hod_email = request.session['hod_email']
    hod = get_object_or_404(HOD, email=hod_email)

    # Fetch only leave requests for faculty in the same department as the HOD
    leave_requests = FacultyLeaveApplication.objects.filter(faculty__department=hod.department)

    return render(request, "HOD/manage_faculty_leave_requests.html", {
        'leave_requests': leave_requests,
        'csrf_token': get_token(request)
    })

# HOD approving a leave request
def approve_leave(request, leave_id):
    leave_request = get_object_or_404(FacultyLeaveApplication, id=leave_id)
    leave_request.status = "Approved"
    leave_request.save()
    messages.success(request, "Leave approved successfully.")
    return redirect('HOD:manage_faculty_leave_requests')

# HOD rejecting a leave request
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(FacultyLeaveApplication, id=leave_id)
    leave_request.status = "Rejected"
    leave_request.save()
    messages.error(request, "Leave rejected.")
    return redirect('HOD:manage_faculty_leave_requests')

