from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
import csv
from google.oauth2 import service_account
# from googleapiclient.discovery import build
from django.contrib.auth import login,logout
from django.shortcuts import render, redirect
from django.shortcuts import redirect,render
from accounts.dbapi import get_user,create_user
from employees.dbapi import create_employee,all_employees,get_employee,filter_employees
from accounts.dbapi import get_user
from .helper import update_db_object,get_date_object,create_reply_message
import os.path
import re
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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

def bulk_employee_registation(request):
    if request.method == 'POST':
        file = request.FILES['employee_file']
        df = pd.DataFrame()

        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        if file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)

        failed_record = list()
        if not df.empty:
            for _, row in df.iterrows():
                try:
                    user = get_user(email=row.get('Email',str()))
                    employee_instance = filter_employees(user_id=user.id).first()
                    if user and employee_instance:
                        failed_record.append(row)
                        continue
                except ObjectDoesNotExist:
                    user = create_user(email=row.get('Email',str()),password=row.get('Password',str()))

            employee_info = {
                "user_id": user.id,
                "name" : row.get('Name',str()),
                "date_of_birth" : get_date_object(row.get('Date_of_Birth',str())),
                "date_of_joining" : get_date_object(row.get('Date_of_Joining',str())),
                "gender" : row.get('Gender',str()),
                "designation" : row.get('Designation',str()),
                "manager" : row.get('Manager',str()),
                # "picture" : request.FILES['picture']
            }

            try:
                employee = create_employee(**employee_info)
            except Exception as e:
                failed_record.append(row)

        if not failed_record:
            return redirect('/login/')
        else:
            messages.error(request, f'Registration of some employee failed')
            return render(request, 'bulk_upload.html')


    return render(request, 'bulk_upload.html')

def get_email_via_gmail(request,employee_id):
    try:
        employee = get_employee(id=int(employee_id))
    except ObjectDoesNotExist:
        return redirect('/get-all-employees/')
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    FILE_NAME="client_secret_445941460366-e7r8modsmln19u8cljheoe4gmhj0orr2.apps.googleusercontent.com.json"
    # SERVICE_ACCOUNT_FILE_NAME="emplist-392218-6706fd3418ec.json"
    # credentials = service_account.Credentials.from_service_account_file(f'/Users/rushikeshsakharwade/Downloads/{SERVICE_ACCOUNT_FILE_NAME}', scopes=SCOPES)
    # service = build('gmail', 'v1', credentials=credentials)
    # print(service)
    # results = service.users().messages().list(userId='rushikeshsakharwade@gmail.com', labelIds=['INBOX']).execute()
    # messages = results.get('messages', [])

    # if not messages:
    #     print('No messages found.')
    # else:
    #     print('Inbox Emails:')
    # for message in messages:
    #     msg = service.users().messages().get(userId='rushikeshsakharwade@gmail.com', id=message['id']).execute()
    #     headers = msg['payload']['headers']
    #     for header in headers:
    #         if header['name'] == 'From':
    #             print(header['value'])
    # from simplegmail import Gmail

    # gmail = Gmail()

    # # Unread messages in your inbox
    # messages = gmail.get_unread_inbox()

    # # Starred messages
    # messages = gmail.get_starred_messages()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'],maxResults=20).execute()
        messages = results.get('messages', [])
        print(messages)
        emails_list = list()
        if messages:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = {
                'from': next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'), ''),
                'subject': next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), ''),
                'body': msg['snippet'],
                'msg_id': message['id']
                }
                emails_list.append(email_data)

    except HttpError as error:
        print(f'An error occurred: {error}')
    
    return render(request, 'display_email_list.html',context={"emails":emails_list,"employee_id":employee_id})

def reply_email(request,email_id,employee_id):
    if request.method == "POST":
        reply_body = request.POST.get('reply',str())

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send']
        
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        

        mime_msg = MIMEMultipart()
   
        try:
            service = build('gmail', 'v1', credentials=creds)
            msg = service.users().messages().get(userId='me', id=email_id).execute()
            mime_msg['to'] = next((re.findall(r'[\w\.-]+@[\w\.-]+', header['value'])[0] for header in msg['payload']['headers'] if header['name'] == 'From'), '')
            mime_msg['subject'] = f"Reply - {next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), '')}"
            mime_msg.attach(MIMEText(reply_body))
            raw_message = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode('utf-8')
            
            service.users().messages().send(userId='me', body={'raw':raw_message}).execute()
        
        except HttpError as error:
            messages.error("Something went wrong !")
            print(f'An error occurred: {error}')
            return render(request,"reply.html",context={"email_id":email_id,"employee_id":employee_id})


        return redirect('get-emails', employee_id=employee_id)
    
    return render(request,"reply.html",context={"email_id":email_id,"employee_id":employee_id})

def callback(request):
    print(request)





        

