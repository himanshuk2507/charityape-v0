def dict_resp(table):
    col_names = list(table.__table__.columns.keys())
    dict_resp = {}
    try:
        for name in col_names:
            dict_resp[name] = getattr(table, name)
        return dict_resp
    except Exception as e:
        return str(e)


def multi_dict_resp(tables):
    data = []
    for table in tables:
        col_names = list(table.__table__.columns.keys())
        dict_resp = {}
        try:
            for name in col_names:
                dict_resp[name] = getattr(table, name)
            data.append(dict_resp)
        except Exception as e:
            return str(e)
    return data
