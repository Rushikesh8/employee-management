from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect,render
from accounts.dbapi import get_user,create_user
from employees.dbapi import create_employee

def employee_registration(request):
    if request.method == 'POST':

        try:
            user = get_user(email=request.POST['email'])
            messages.error(request, 'Username already exists')
            return render(request, 'registration.html')
        except ObjectDoesNotExist:
            user = create_user(email=request.POST['email'],password=request.POST['password'])
        
        employee_info = {
            "user_id": user.id,
            "email" : request.POST['email'],
            "password" : request.POST['password'],
            "name" : request.POST['name'],
            "date_of_birth" : request.POST['date_of_birth'],
            "date_of_joining" : request.POST['date_of_joining'],
            "gender" : request.POST['gender'],
            "designation" : request.POST['designation'],
            "manager" : request.POST['manager'],
            "picture" : request.FILES['picture']
        }

        try:
            create_employee(**employee_info)
            # return redirect('login')
        except Exception as e:
             return render(request, 'registration.html')

        
    
    return render(request, 'registration.html')



        

