from .models import CustomUser

def get_user(*args,**kwargs) -> CustomUser:
    return CustomUser.objects.get(*args,**kwargs)

def create_user(*args,**kwargs) -> CustomUser:
    return CustomUser.objects.create(*args,**kwargs)

