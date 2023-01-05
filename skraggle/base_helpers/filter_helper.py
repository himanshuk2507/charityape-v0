from skraggle.config import db


def get_filter_clause(table, column, condition, value):
    if condition == 'gt':
        return getattr(table, column) > value
    elif condition == 'lt':
        return getattr(table, column) < value
    elif condition == 'gte':
        return getattr(table, column) >= value
    elif condition == 'lte':
        return getattr(table, column) <= value
    elif condition == 'eq':
        return getattr(table, column) == value
    elif condition == 'neq':
        return getattr(table, column) != value
    elif condition == 'between':
        return getattr(table, column).between(value.start, value.end)
    elif condition == 'not_between':
        return not getattr(table, column).between(value.start, value.end)
    elif condition == 'in':
        return getattr(table, column).in_(value)
    elif condition == 'not_in':
        return getattr(table, column).not_in(value)
    elif condition == 'null':
        return getattr(table, column).is_(None)
    elif condition == 'not_null':
        return getattr(table, column).is_not(None)
    elif condition == 'matches':
        return getattr(table, column).ilike(f'%{value}%')
