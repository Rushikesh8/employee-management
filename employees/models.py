from django.db import models
from accounts.models import CustomUser

class Employee(models.Model):
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('O','Others')
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    designation = models.CharField(max_length=100)
    manager = models.CharField(max_length=150)
    picture = models.ImageField(upload_to='employee_pictures',null=True,blank=True)
