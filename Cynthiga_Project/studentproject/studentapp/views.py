import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login# Login
from django.contrib import messages #for pop message
from django.contrib.auth.decorators import login_required # Login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count #for Dashboard
from .models import Student
from django.db import IntegrityError


# for extra details

def student_detail(request, id):
    student = get_object_or_404(Student, id=id)
    return render(request, 'student_detail.html', {'student': student})
#  login page
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')   # 🔥 change here
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')
# Home page
@login_required
def home(request):
    return render(request, 'home.html')

# Add student
# def add_student(request):
#     error = None
#     if request.method == 'POST':
#         name = request.POST['name']
#         # roll = request.POST['roll']
#         # dept = request.POST['dept']
#         year = request.POST['year']
#         roll_no = request.POST['roll_no']
#         department = request.POST['department']
#         phone = request.POST.get('phone')
#         address = request.POST.get('address')
#         joining_date = request.POST.get('joining_date')
#         graduation_date = request.POST.get('graduation_date')

#         # Check for duplicate roll number
#         if Student.objects.filter(roll_no=roll_no).exists():
#             error = 'Roll number already exists!'
#         else:
#             Student.objects.create(
#                 name=name,
#                 roll_no=roll_no,
#                 department= department,
#                 year=year,
#                 phone=phone,
#                 address=address,
#                 joining_date=joining_date,
#                 graduation_date=graduation_date
#             )
#             messages.success(request, "Student added successfully!") #for popup message
#             return redirect('view')

#     return render(request, 'add.html', {'error': error})
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_no = request.POST.get('roll_no')
        department = request.POST.get('department')
        year = request.POST.get('year')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        joining_date = request.POST.get('joining_date')
        graduation_date = request.POST.get('graduation_date')

        # ✅ Check empty roll_no
        if not roll_no:
            messages.error(request, "Roll number is required!")
            return redirect('add')

        # ✅ Convert to integer safely
        try:
            roll_no = int(roll_no)
        except ValueError:
            messages.error(request, "Roll number must be a number!")
            return redirect('add')

        # ✅ Check duplicate
        if Student.objects.filter(roll_no=roll_no).exists():
            messages.error(request, "Roll number already exists!")
            return redirect('add')

        # ✅ Save data
        Student.objects.create(
            name=name,
            roll_no=roll_no,
            department=department,
            year=year,
            phone=phone,
            address=address,
            joining_date=joining_date,
            graduation_date=graduation_date
        )

        messages.success(request, "Student added successfully!")
        return redirect('view')

    return render(request, 'add.html')



from django.db.models import Q
def view_students(request):

    query = request.GET.get('q')

    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) |
            Q(roll_no__icontains=query)
        )
    else:
        students = Student.objects.all().order_by('roll_no')

    # ✅ ADD THIS BLOCK HERE
    for s in students:
      if s.total_marks > 0:
        s.percentage = (s.obtained_marks / s.total_marks) * 100
    else:
        s.percentage = 0

    deleted_students = request.session.get('deleted_students', {})

    last_deleted = None
    if deleted_students:
        last_key = list(deleted_students.keys())[-1]
        last_deleted = deleted_students[last_key]

    context = {
        "students": students,
        "last_deleted": last_deleted
    }

    return render(request, "view.html", context)

# Edit student
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    error = None
    if request.method == "POST":
        roll = request.POST['roll']
        # Check duplicate roll number except for this student
        if Student.objects.filter(roll_no=roll).exclude(id=student.id).exists():
            error = 'Roll number already exists!'
        else:
            student.name = request.POST['name']
            student.roll_no = roll
            student.department = request.POST['dept']
            student.year = request.POST['year']
            student.save()
            messages.success(request, "Student updated successfully!") #popup message
            return redirect('view')

    return render(request, 'edit.html', {'student': student, 'error': error})




def delete_student(request, id):
    student = Student.objects.get(id=id)

    # 🔥 force session creation
    if 'deleted_students' not in request.session:
        request.session['deleted_students'] = {}

    deleted_students = request.session['deleted_students']

    deleted_students[str(id)] = {
        'id': student.id,
        'name': student.name,
        'roll_no': student.roll_no,
        'department': student.department,
        'year': student.year
    }

    request.session['deleted_students'] = deleted_students

    # ✅ FORCE SAVE SESSION
    request.session.modified = True

    # 🔥 DEBUG (check terminal)
    print("SESSION DATA:", request.session['deleted_students'])

    student.delete()

    return redirect('view')

import json

def dashboard(request):
    total_students = Student.objects.count()

    dept_data = Student.objects.values('department').annotate(count=Count('department'))

    labels = [d['department'] for d in dept_data]
    counts = [d['count'] for d in dept_data]

    context = {
        'total_students': total_students,
        'dept_labels': json.dumps(labels),   # ✅ convert to JSON
        'dept_counts': json.dumps(counts),   # ✅ convert to JSON
    }

    return render(request, 'dashboard.html', context)



def undo_student(request, id):
    deleted_students = request.session.get('deleted_students', {})
    student_data = deleted_students.get(str(id))

    if student_data:
        Student.objects.create(
            name=student_data['name'],
            roll_no=student_data['roll_no'],
            department=student_data['department'],
            year=student_data['year']
        )

        del deleted_students[str(id)]
        request.session['deleted_students'] = deleted_students

        request.session.modified = True   # ✅
        request.session.save()            # ✅

    return redirect('view')