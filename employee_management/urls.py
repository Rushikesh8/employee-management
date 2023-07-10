"""employee_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from employees.views import (employee_registration,
                             employee_login,
                             get_all_employees,
                             edit_employee,
                             delete_employee,
                             logout_view,
                             export_employee,
                             employee_search,
                             bulk_employee_registation,
                             get_email_via_gmail,
                             reply_email,
                             callback)

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('employee-registration/', employee_registration, name="employee-registration"),
    path('login/', employee_login, name="login"),
    path('logout/', logout_view, name="logout"),
    path('get-all-employees/', get_all_employees, name="get-all-employees"),
    path('edit-employee/<str:employee_id>/', edit_employee, name="edit-employee"),
    path('delete-employee/<str:employee_id>/', delete_employee, name="delete-employee"),
    path('export-employees/', export_employee, name="export-employees"),
    path('search-employees/', employee_search, name="search-employees"),
    path('bulk-employee-registration/', bulk_employee_registation, name="bulk-employee-registration"),
    path('get-emails/<str:employee_id>/',get_email_via_gmail,name="get-emails"),
    path('reply-email/<str:email_id>/<str:employee_id>/',reply_email,name="reply-email"),
    path('callback',callback,name="callback")

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
