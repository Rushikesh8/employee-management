from datetime import datetime,date
from django.utils.timezone import make_aware
import base64

def update_db_object(db_object:object,update_data:dict) -> object:
    for attribute,value in update_data.items():
        if value:
            setattr(db_object,attribute,value)
    db_object.save()
    return db_object

def get_date_object(date_str:str) -> object:
    if not date_str:
        return str()
    day,month,year = list(map(int,date_str.split("/")))
    date_obj = date(year=year,month=month,day=day)
    # date_obj = datetime.strptime(date_str, '%d/%m/%y').date()
    # date_field = make_aware(date_obj)
    return date_obj

def create_reply_message(original_message, reply_body):
    reply_message = {
        'threadId': original_message['threadId'],
        'labelIds': original_message['labelIds'],
        'raw': base64.urlsafe_b64encode(reply_body.encode()).decode()
    }
    return reply_message
    