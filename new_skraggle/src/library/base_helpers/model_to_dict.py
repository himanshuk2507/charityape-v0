def model_to_dict(model):
    '''
    Converts an SQLAlchemy Model object to a dictionary.
    '''
    if not model:
        return None
        
    columns = list(model.__table__.columns.keys())
    map = {}
    try:
        for field in columns:
            map[field] = getattr(model, field)
        return map 
    except Exception as e:
        return str(e)