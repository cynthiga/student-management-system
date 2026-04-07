from django.urls import path
from . import views

urlpatterns = [
    # 🔓 Login first page
    path('', views.login_view, name='login'),

    # 🔐 After login
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # 🔐 Student CRUD
    path('add/', views.add_student, name='add'),
    path('view/', views.view_students, name='view'),
    path('edit/<int:id>/', views.edit_student, name='edit'),
    path('delete/<int:id>/', views.delete_student, name='delete'),
    path('undo/<int:id>/', views.undo_student, name='undo'),
    # path('students/', views.student_list, name='student_list'),
    path('student/<int:id>/', views.student_detail, name='student_detail'),
    
]