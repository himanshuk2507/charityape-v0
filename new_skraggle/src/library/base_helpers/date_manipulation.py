from datetime import datetime


def days_between_dates(date_1: datetime = None, date_2: datetime = None):
    '''
    Calculate the number of days between two dates.
    '''
    if date_1 is None:
        raise Exception('date_1 cannot be NoneType')
    if date_2 is None:
        raise Exception('date_2 cannot be NoneType')
    return (date_1 - date_2).days


def days_left_until(date: datetime = None):
    '''
    Calculate the number of days between the current date and a future or past date. Equivalent to `days_between_dates(datetime.now(), date).`
    '''
    return days_between_dates(date, datetime.now())


def hours_between_dates(date_1: datetime = None, date_2: datetime = None):
    '''
    Calculate the number of hours between two dates.
    '''
    if date_1 is None:
        raise Exception('date_1 cannot be NoneType')
    if date_2 is None:
        raise Exception('date_2 cannot be NoneType')
    hours = (date_1 - date_2).total_seconds() / 3600
    return int(f'{hours:.0f}')


def hours_left_until(date: datetime = None):
    '''
    Calculate the number of hours between the current date and a future or past date. Equivalent to `hours_between_dates(datetime.now(), date).`
    '''
    return hours_between_dates(date, datetime.now())