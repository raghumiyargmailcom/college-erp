from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
import pandas as pd
from django.contrib.auth.hashers import make_password,check_password
from django.http import JsonResponse
from .models import Childrens, Faculty, HOD, Principal, ExamSchedule, Subject
from django.views.decorators.http import require_http_methods

from django.views.decorators.csrf import csrf_protect,csrf_exempt
import json 
import re
from django.utils import timezone


def home(request):
    """Simple home page view."""
    return render(request, 'home.html')
def user_login(request):
    if request.method == 'POST':  # Only handle POST requests
        username = request.POST['username']  # Ensures KeyError if missing
        password = request.POST['password']

        # Authenticate user (Controll app login)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_home')  # Redirect to Admin Home

        messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')  # Show login page after failed login
# ✅ Add this function to prevent AttributeError
def admin_home(request):
    return render(request, 'admin_home.html')  # Ensure 'admin_home.html' exists in templates

def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('login')
     
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from controll.models import Childrens, HOD, Faculty  # Make sure Faculty is imported

def student_login(request):
    """Authenticate Students, HODs, and Faculty, and create a session."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"🔍 Login Attempt: {email}")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from controll.models import Childrens, HOD, Faculty

def student_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        print(f"🔍 Login attempt with: {email}")

        # 1. Check Student
        student = Childrens.objects.filter(email__iexact=email).first()
        if student:
            if check_password(password, student.password):
                request.session.flush()
                request.session["student_rollno"] = student.rollno
                request.session["student_email"] = student.email
                request.session["student_department"] = student.department
                request.session.set_expiry(0)
                return redirect("student:student_dashboard")
            else:
                messages.error(request, "Incorrect password.")
                return redirect("login")

        # 2. Check HOD
        hod = HOD.objects.filter(email__iexact=email).first()
        if hod:
            if check_password(password, hod.password):
                request.session.flush()
                request.session["hod_id"] = hod.hod_id
                request.session["hod_email"] = hod.email
                request.session["hod_department"] = hod.department
                request.session.set_expiry(0)
                return redirect("HOD:hod_dashboard")
            else:
                messages.error(request, "Incorrect password.")
                return redirect("login")

        # 3. Check Faculty
        faculty = Faculty.objects.filter(email__iexact=email).first()
        print(f"🧑‍🏫 Faculty fetched: {faculty}")  # Debug print
        if faculty:
            print(f"🔑 Faculty password hash: {faculty.password}")  # Debug print
            if check_password(password, faculty.password):
                request.session.flush()
                request.session["faculty_id"] = faculty.faculty_id
                request.session["faculty_email"] = faculty.email
                request.session["faculty_department"] = faculty.department
                request.session.set_expiry(0)
                return redirect("faculty:faculty_dashboard")
            else:
                messages.error(request, "Incorrect password.")
                return redirect("login")

        # If no match
        messages.error(request, "Invalid email or password.")
        return redirect("login")

    return render(request, "student_login.html")




# ---------------- STUDENT MANAGEMENT (Unchanged) ----------------


def import_students(request):
    """Imports student data from an Excel file."""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            df = pd.read_excel(excel_file)

            required_columns = {'rollno', 'name', 'email', 'class_name', 'department', 'password'}
            if not required_columns.issubset(df.columns):
                messages.error(request, "Incorrect Excel format for students.")
                return redirect('import_students')

            students_to_add = []
            for _, row in df.iterrows():
                rollno = str(row.get('rollno')).strip()
                name = str(row.get('name')).strip()
                email = str(row.get('email')).strip()
                class_name = str(row.get('class_name')).strip()
                department = str(row.get('department')).strip()  # ✅ Import department
                password = str(row.get('password')).strip()

                if not Childrens.objects.filter(rollno=rollno).exists():
                    students_to_add.append(Childrens(
                        rollno=rollno,
                        name=name,
                        email=email,
                        class_name=class_name,
                        department=department,
                        password=make_password(password)
                    ))

            if students_to_add:
                Childrens.objects.bulk_create(students_to_add)
                messages.success(request, "Students imported successfully!")
            else:
                messages.warning(request, "No new students added.")

            return redirect('manage_students')

        except Exception as e:
            messages.error(request, f"Error importing students: {e}")
            return redirect('import_students')

    return render(request, 'import_students.html')
#MANAGE STUDENT
@login_required(login_url='login')
def manage_students(request):
    """Displays all Childrens records."""
    students = Childrens.objects.all()
    return render(request, 'manage_student.html', {'students': students})
@csrf_exempt  # Temporarily disable CSRF to check if it’s causing the issue
@login_required(login_url='login')
def update_student(request):
    """Updates student details via AJAX."""
    if request.method == "POST":
        print("Received Update Request Data:", request.POST)  # Debugging

        rollno = request.POST.get("rollno")
        if not rollno:
            return JsonResponse({"success": False, "message": "Roll number is required."})

        try:
            student = Childrens.objects.get(rollno=rollno)

            # Update fields from the request, keeping existing values if not provided
            student.name = request.POST.get("name", student.name)
            student.email = request.POST.get("email", student.email)
            student.class_name = request.POST.get("class_name", student.class_name)
            student.department = request.POST.get("department", student.department)  # ✅ Added Department Field
            student.phone_number = request.POST.get("phone_number", student.phone_number)
            student.address = request.POST.get("address", student.address)

            # Handle password update
            new_password = request.POST.get("password")
            if new_password:
                student.password = make_password(new_password)  # Hash the new password

            # Handle profile photo update
            if 'profile_photo' in request.FILES:
                student.profile_photo = request.FILES['profile_photo']

            student.save()
            return JsonResponse({"success": True, "message": "Student updated successfully!"})

        except Childrens.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student record not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error updating student: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})
#DELETE STUDENT
@csrf_exempt  # Temporarily disable CSRF for testing (Remove this in production)
@login_required(login_url='login')
def delete_student(request):
    """Deletes a student via AJAX."""
    if request.method == "POST":
        print("Received Delete Request Data:", request.POST)  # Debugging

        rollno = request.POST.get("rollno")
        if not rollno:
            return JsonResponse({"success": False, "message": "Roll number is required."})

        try:
            student = get_object_or_404(Childrens, rollno=rollno)
            student.delete()
            return JsonResponse({"success": True, "message": f"Student {rollno} deleted successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error deleting student: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})
# ---------------- FACULTY MANAGEMENT (Unchanged) ----------------
@login_required(login_url='login')
def import_faculty(request):
    """Imports faculty data from an Excel file."""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            df = pd.read_excel(excel_file)

            required_columns = {'faculty_id', 'name', 'email', 'department', 'password'}
            if not required_columns.issubset(df.columns):
                messages.error(request, "Incorrect Excel format for faculty.")
                return redirect('import_faculty')

            faculty_to_add = []
            for _, row in df.iterrows():
                faculty_id = str(row.get('faculty_id')).strip()
                name = str(row.get('name')).strip()
                email = str(row.get('email')).strip()
                department = str(row.get('department')).strip()
                password = str(row.get('password')).strip()

                if not Faculty.objects.filter(faculty_id=faculty_id).exists():
                    faculty_to_add.append(Faculty(
                        faculty_id=faculty_id,
                        name=name,
                        email=email,
                        department=department,
                        password=make_password(password)
                    ))

            if faculty_to_add:
                Faculty.objects.bulk_create(faculty_to_add)
                messages.success(request, "Faculty imported successfully!")
            else:
                messages.warning(request, "No new faculty members added.")

            return redirect('manage_faculty')

        except Exception as e:
            messages.error(request, f"Error importing faculty: {e}")
            return redirect('import_faculty')

    return render(request, 'import_faculty.html')

@login_required(login_url='login')
def manage_faculty(request):
    """Displays all Faculty records."""
    faculties = Faculty.objects.all()
    return render(request, 'manage_faculty.html', {'faculties': faculties})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Faculty  # Update if your model is in a different app

@require_POST
@csrf_exempt  # Optional if you're not handling CSRF in headers; better to use @csrf_protect with correct token in JS
def update_faculty(request):
    faculty_id = request.POST.get("faculty_id")
    name = request.POST.get("name")
    email = request.POST.get("email")
    department = request.POST.get("department")
    password = request.POST.get("password")

    if not all([faculty_id, name, email, department]):
        return JsonResponse({"success": False, "error": "Missing required fields."})

    try:
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        faculty.name = name
        faculty.email = email
        faculty.department = department
        if password:
            faculty.set_password(password)
        faculty.save()
        return JsonResponse({"success": True})
    except Faculty.DoesNotExist:
        return JsonResponse({"success": False, "error": "Faculty not found."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required(login_url='login')
def delete_faculty(request, faculty_id):
    """Deletes a Faculty record directly from the Manage Faculty page."""
    try:
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        faculty.delete()
        return JsonResponse({"success": True})
    except Faculty.DoesNotExist:
        return JsonResponse({"success": False, "error": "Faculty record not found."})

# ---------------- HOD MANAGEMENT (Newly Added) ----------------
@login_required(login_url='login')
def add_hod(request):
    if request.method == "POST":
        hod_id = request.POST.get("hod_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        department = request.POST.get("department")
        password = request.POST.get("password")

        # 1. HOD ID: max 6 alphanumeric
        if not re.match(r'^[A-Za-z0-9]{1,6}$', hod_id):
            messages.error(request, "HOD ID must be alphanumeric and up to 6 characters.")
            return redirect('add_hod')

        # 2. Name: only letters, up to 20 chars
        if not re.match(r'^[A-Za-z]{1,20}$', name):
            messages.error(request, "Name must contain only letters (up to 20 characters).")
            return redirect('add_hod')

        # 3. Email: must end with @gmail.com
        if not email.endswith("@gmail.com"):
            messages.error(request, "Email must end with @gmail.com.")
            return redirect('add_hod')

        # 4. Check if email already exists
        if HOD.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('add_hod')

        # 5. Password: Uppercase, lowercase, digit, special char, min 6 chars
        if len(password) < 6 or \
           not re.search(r'[A-Z]', password) or \
           not re.search(r'[a-z]', password) or \
           not re.search(r'[0-9]', password) or \
           not re.search(r'[\W_]', password):
            messages.error(request, "Password must be at least 6 characters and include uppercase, lowercase, digit, and special character.")
            return redirect('add_hod')

        # All validations passed – create HOD
        HOD.objects.create(
            hod_id=hod_id,
            name=name,
            email=email,
            department=department,
            password=make_password(password)
        )
        messages.success(request, "HOD added successfully!")
        return redirect('manage_hod')

    return render(request, 'add_hod.html')

@login_required(login_url='login')
def manage_hod(request):
    """Displays all HOD records."""
    hods = HOD.objects.all()
    return render(request, 'manage_hod.html', {'hods': hods})

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import HOD

@login_required(login_url='login')
def update_hod(request, hod_id):  # Accepts hod_id from the URL
    """Handles AJAX request to update an HOD's details."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        department = request.POST.get("department")
        password = request.POST.get("password")

        try:
            hod = get_object_or_404(HOD, hod_id=hod_id)  # FIXED LINE
            hod.name = name
            hod.email = email
            hod.department = department
            if password:
                hod.set_password(password)
            hod.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@login_required(login_url='login')
def delete_hod(request, hod_id):
    """Deletes an HOD record."""
    try:
        hod = get_object_or_404(HOD, hod_id=hod_id)  # Ensure correct lookup field
        hod.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})  # Shows actual error message
    # ---------------- PRINCIPAL MANAGEMENT ----------------
@login_required(login_url='login')
def add_principal(request):
    """Manually adds a Principal."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if Principal.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('add_principle')

        Principal.objects.create(
            name=name,
            email=email,
            password=make_password(password)
        )
        messages.success(request, "Principal added successfully!")
        return redirect('manage_principle')

    return render(request, 'add_principle.html')

@login_required(login_url='login')
def manage_principal(request):
    """Displays all Principal records."""
    principals = Principal.objects.all()
    return render(request, 'manage_principle.html', {'principals': principals})

@login_required(login_url='login')
def delete_principal(request, principal_id):
    """Deletes a Principal via AJAX."""
    try:
        principal = Principal.objects.get(principal_id=principal_id)
        principal.delete()
        return JsonResponse({"success": True})
    except Principal.DoesNotExist:
        return JsonResponse({"success": False, "error": "Principal record not found."})

@login_required(login_url='login')
def update_principal(request, principal_id):
    """Updates a Principal's details via AJAX."""
    if request.method == "POST":
        try:
            principal = Principal.objects.get(principal_id=principal_id)
            principal.name = request.POST.get("name")
            principal.email = request.POST.get("email")
            principal.save()
            return JsonResponse({"success": True})
        except Principal.DoesNotExist:
            return JsonResponse({"success": False, "error": "Principal not found."})

    return JsonResponse({"success": False, "error": "Invalid request method."})
#exam Schedule management
    
@login_required
def schedule_exam(request):
    if request.method == "POST":
        course = request.POST.get("course", "").strip()
        exam_date = request.POST.get("exam_date", "").strip()
        start_time = request.POST.get("start_time", "").strip()
        end_time = request.POST.get("end_time", "").strip()
        hall = request.POST.get("hall", "").strip()

        # Check if all fields are filled
        if not all([course, exam_date, start_time, end_time, hall]):
            return JsonResponse({"success": False, "message": "All fields are required."})

        # Check if exam date is in the future
        try:
            exam_date_obj = timezone.datetime.strptime(exam_date, "%Y-%m-%d").date()
            if exam_date_obj <= timezone.now().date():
                return JsonResponse({"success": False, "message": "Exam date must be in the future."})
        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid exam date format."})

        # Validate exam hall: only letters and numbers allowed
        if not re.match(r'^[A-Za-z0-9 ]+$', hall):
            return JsonResponse({"success": False, "message": "Exam hall must contain only letters and numbers."})

        # Save the data
        try:
            ExamSchedule.objects.create(
                course=course,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                hall=hall
            )
            return JsonResponse({"success": True, "message": "Exam scheduled successfully!"})
        except Exception:
            return JsonResponse({"success": False, "message": "Failed to schedule exam. Try again."})

    return render(request, "schedule_exam.html")
@login_required
def manage_exam_schedule(request):
    exams = ExamSchedule.objects.all().order_by("exam_date")
    return render(request, "manage_exam_schedule.html", {"exams": exams})

@csrf_exempt  
@login_required
def update_exam(request, exam_id):
    try:
        print(f"Received Update Request for Exam ID: {exam_id}")  # Debugging
        data = json.loads(request.body.decode("utf-8"))
        print("Received Data:", data)  # Debugging

        exam = get_object_or_404(ExamSchedule, exam_id=exam_id)
        print("Exam Found:", exam)  # Debugging

        if data.get("course"):
            exam.course = data["course"]
        if data.get("exam_date"):  
            exam.exam_date = data["exam_date"]
        if data.get("start_time"):  
            exam.start_time = data["start_time"]
        if data.get("end_time"):  
            exam.end_time = data["end_time"]
        if data.get("hall"):
            exam.hall = data["hall"]

        exam.save()
        print("Exam Updated Successfully!")  # Debugging
        return JsonResponse({"success": True, "message": "Exam updated successfully!"})

    except Exception as e:
        print("Error Updating Exam:", str(e))  # Debugging
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt  # Temporarily disable CSRF (use CSRF tokens instead if needed)
@login_required
def delete_exam(request, exam_id):
    try:
        print(f"Attempting to delete exam ID: {exam_id}")  # Debugging output
        exam = get_object_or_404(ExamSchedule, exam_id=exam_id)
        exam.delete()
        print(f"Deleted Exam: {exam_id}")  # Debugging output

        return JsonResponse({"success": True, "message": "Exam deleted successfully!"})

    except Exception as e:
        print(f"Error Deleting Exam {exam_id}:", str(e))  # Debugging output
        return JsonResponse({"success": False, "error": str(e)})
    

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subject
import json

def subject_list(request):
    """Render the subject list template with all subjects."""
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})  # Ensure correct template path


@csrf_exempt
def add_subject(request):
    """Handles both GET (render form) and POST (add subject)."""

    if request.method == 'GET':
        return render(request, 'add_subject.html')  # Ensure this template exists

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        department = request.POST.get('department')
        semester = request.POST.get('semester')

        if not all([name, code, department, semester]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        Subject.objects.create(name=name, code=code, department=department, semester=semester)
        return JsonResponse({'message': 'Subject added successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
@csrf_exempt
def update_subject(request, subject_id):
    """Update an existing subject's details via a POST request."""
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            subject.name = data.get('name', subject.name)
            subject.code = data.get('code', subject.code)
            subject.department = data.get('department', subject.department)
            subject.semester = data.get('semester', subject.semester)
            subject.save()
            return JsonResponse({'message': 'Subject updated successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_subject(request, subject_id):
    """Delete a subject via a POST request."""
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == 'POST':
        subject.delete()
        return JsonResponse({'message': 'Subject deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
