from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Q
import csv
from django.contrib.auth import login,logout
from django.shortcuts import render, redirect
from django.shortcuts import redirect,render
from accounts.dbapi import get_user,create_user
from employees.dbapi import create_employee,all_employees,get_employee,filter_employees
from accounts.dbapi import get_user
from .helper import update_db_object

def employee_login(request):
    if request.method != "POST" and request.user.is_anonymous:
        return render(request, 'login.html')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = get_user(email=email)
        except ObjectDoesNotExist:
            user = None


        if user and user.password == password.strip() and user.is_active:
            login(request, user)
            return redirect('/get-all-employees/') 
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'login.html')

    return render(request, 'login.html')

def get_all_employees(request):
    employees = list()
    if not request.user.is_anonymous:
        employees = all_employees()
    return render(request, 'home_page.html', context={"employees":employees})


def employee_search(request):
    query = request.GET.get('search')
    if query:
        employees = filter_employees(Q(name__icontains=query))
    else:
        employees = all_employees()
    return render(request, 'home_page.html', context={"employees":employees})

def edit_employee(request,employee_id):
    if request.user.is_anonymous:
        return redirect('/login/')
    
    try:
        employee = get_employee(id=employee_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Employee does not exist')
        employees = all_employees()
        return render(request, 'home_page.html', context={"employees":employees})
    
    if request.method == 'POST' and employee:
        update_db_object(employee,request.POST)
        return redirect('/get-all-employees/')
    
    return render(request,'edit.html',context={"employee":employee})

def delete_employee(request,employee_id):
    if request.user.is_anonymous:
        return redirect('/login/')
    
    try:
        employee = get_employee(id=employee_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Employee does not exist')
        employees = all_employees()
        return render(request, 'home_page.html', context={"employees":employees})
    
    if employee:
        employee.delete()
    
    return redirect('/get-all-employees/')
    
def logout_view(request):
    logout(request)
    return redirect('/login/')



def employee_registration(request):
    if request.method == 'POST':

        try:
            user = get_user(email=request.POST['email'])
            messages.error(request, 'User with email already exists')
            return render(request, 'registration.html')
        except ObjectDoesNotExist:
            user = create_user(email=request.POST['email'],password=request.POST['password'])
        
        employee_info = {
            "user_id": user.id,
            # "email" : request.POST['email'],
            # "password" : request.POST['password'],
            "name" : request.POST['name'],
            "date_of_birth" : request.POST['date_of_birth'],
            "date_of_joining" : request.POST['date_of_joining'],
            "gender" : request.POST['gender'],
            "designation" : request.POST['designation'],
            "manager" : request.POST['manager'],
            "picture" : request.FILES['picture']
        }

        try:
            user = create_employee(**employee_info)
        except Exception as e:
             messages.error(request, 'Error while registering employee')
             return render(request, 'registration.html')
        
        if user:
            return redirect('/login/')

    return render(request, 'registration.html')

def export_employee(request):
    if request.user.is_anonymous:
        return redirect('/login/')
    
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="employee.csv"'
    writer = csv.writer(response)
    headrow = ["Name","Date of Birth","Date of Joining","Gender","Designation","Manager","Email"]
    writer.writerow(headrow)
    employees = all_employees()
    if employees.exists():
        for employee in employees.iterator():
            row = [
                employee.name,
                employee.date_of_birth,
                employee.date_of_joining,
                employee.gender,
                employee.designation,
                employee.manager,
                employee.user.email
            ]
            writer.writerow(row)
    return response









        

