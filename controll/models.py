from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

# ------------------ Students Model ------------------


class Childrens(models.Model):  # ✅ Kept 'Childrens' as per your request
    rollno = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    class_name = models.CharField(max_length=50)
    department = models.CharField(max_length=50, blank=True, null=True)  # ✅ Allow existing records to have NULL values
  # ✅ Added department field (Imported from Excel)
    password = models.CharField(max_length=255)  # Store hashed password
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(Childrens, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.rollno} - {self.name} ({self.department})"




# ------------------ Faculty Model ------------------
class Faculty(models.Model):
    faculty_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Store hashed password

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(Faculty, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.faculty_id} - {self.name}"

# ------------------ HOD Model ------------------
class HOD(models.Model):
    hod_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Store hashed password

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hod_id} - {self.name}"

class Childrens(models.Model):  # ✅ Kept 'Childrens' as per your request
    rollno = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    class_name = models.CharField(max_length=50)
    department = models.CharField(max_length=50, blank=True, null=True)  # ✅ Allow existing records to have NULL values
    password = models.CharField(max_length=255)  # Store hashed password
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # ✅ Added ForeignKey relation with HOD (Each child belongs to one HOD)
    hod = models.ForeignKey(HOD, on_delete=models.SET_NULL, null=True, blank=True, related_name="children")

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(Childrens, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.rollno} - {self.name} ({self.department})"


# ------------------ Principal Model ------------------
class Principal(models.Model):
    principal_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed password

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(Principal, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Principal)"

# ------------------ Exam Schedule Model ------------------
class ExamSchedule(models.Model):
    exam_id = models.AutoField(primary_key=True)  # Auto-increment ID for exams
    course = models.CharField(max_length=100)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hall = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.course} - {self.exam_date} ({self.start_time} to {self.end_time})"
    


    #time table



    #leave model
    from django.db import models

class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey('Childrens', on_delete=models.CASCADE)
    hod = models.ForeignKey('HOD', on_delete=models.CASCADE)
    reason = models.TextField()
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.status}"
    


    
from django.db import models

class Subject(models.Model):
    DEPARTMENT_CHOICES = [
        ('mca', 'mca'),
        ('MBA', 'MBA'),
    ]

    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
    ]

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=3, choices=DEPARTMENT_CHOICES)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.department} Sem {self.semester}"


class Marks(models.Model):
    student = models.ForeignKey(Childrens, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    semester = models.CharField(max_length=1, choices=[
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
    ])
    marks_obtained = models.IntegerField()
    total_marks = models.IntegerField(default=100)  # Keeping total_marks as it is
    max_marks = models.IntegerField(default=100)  # New column for max marks

    class Meta:
        unique_together = ('student', 'subject', 'semester')  # Each student can have only one record per subject per semester

    def __str__(self):
        return f"{self.student.rollno} - {self.subject.name} - {self.marks_obtained}/{self.max_marks}"


class FacultyLeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    hod = models.ForeignKey('HOD', on_delete=models.CASCADE)
    reason = models.TextField()
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty.name} - {self.status}"
    

from django.db import models

class Attendance(models.Model):
    student = models.ForeignKey('Childrens', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    status = models.CharField(max_length=1)  # 'P' or 'A'
    date = models.DateField()
