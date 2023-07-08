from .models import Employee
from django.db.models import QuerySet

def create_employee(*args,**kwargs) -> Employee:
    return Employee.objects.create(*args,**kwargs)

def all_employees() -> QuerySet:
    return Employee.objects.all()

def get_employee(*args,**kwargs) -> Employee:
    return Employee.objects.get(*args,**kwargs)

def filter_employees(*args,**kwargs) -> QuerySet:
    return Employee.objects.filter(*args,**kwargs)
