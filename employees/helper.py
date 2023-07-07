def update_db_object(db_object:object,update_data:dict) -> object:
    for attribute,value in update_data.items():
        if value:
            setattr(db_object,attribute,value)
    db_object.save()
    return db_object