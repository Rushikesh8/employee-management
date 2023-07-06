from .models import Employee

def create_employee(*args,**kwargs) -> Employee:
    return Employee.objects.create(*args,**kwargs)