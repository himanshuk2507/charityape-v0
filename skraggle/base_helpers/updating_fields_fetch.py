from skraggle.config import db


def get_fields(table, ignore=True):
    col_names = list(table.__table__.columns.keys())

    if ignore:
        ignore_fields = [list(table.__table__.primary_key)[0].name, "organization_id"]
        updating_fields = [x for x in col_names if x not in ignore_fields]
        return updating_fields
    else:
        ignore_fields = [list(table.__table__.primary_key)[0].name]
        updating_fields = [x for x in col_names if x not in ignore_fields]
        return updating_fields


def normalize_db_fields(fields):
    try:
        [
            field.update(
                {
                    "field_type": "".join(
                        repr(field["field_type"]).partition("(")[0]
                    ).lower()
                }
            )
            for field in fields
        ]
        return fields
    except Exception as e:
        return str(e)
