from datetime import datetime

from dateutil import parser
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt
from sqlalchemy import and_
from skraggle.base_helpers.updating_fields_fetch import normalize_db_fields
from skraggle.campaigns.models import Campaigns
from skraggle.contact.Fundraising.models import Transactions
from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import multi_dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.contact.models import (
    SegmentUsers,
    ContactUsers,
    HouseholdUsers,
    TagUsers,
    CompanyUsers,
)

from skraggle.donation.models import Pledges, ScheduleRecurringDonation, TransactionDonation
from skraggle.eblasts.models import Eblasts
from skraggle.config import db, engine
from skraggle.forms.models import Forms
import pandas as pd
import io
from sqlalchemy.inspection import inspect

globalendpoints = Blueprint("globalendpoints", __name__)


# Api to fetch Contact Details by passing List of Contact ID's
# parameter json-format  : {"contacts":[id1,id2,id3]}


@globalendpoints.route("/contact_details", methods=["GET"])
@user_required()
def contact_fetcher():
    contact_ids = request.json.get("contacts")
    if contact_ids:
        try:
            contacts = ContactUsers.query.where(
                and_(
                    ContactUsers.organization_id == getOrg(get_jwt()),
                    ContactUsers.id.in_(contact_ids),
                )
            ).all()
            if not contacts:
                resp = DataResponse(False, "No Data to Display")
                return resp.status()

            resp = multi_dict_resp(contacts)
            return jsonify(resp), 200

        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    resp = DataResponse(False, "No Contact ids to fetch details")
    return resp.status()


# Api to fetch all Contact ID's
@globalendpoints.route("/contact_list", methods=["GET"])
@user_required()
def contact_lister():
    try:
        print(getOrg(get_jwt()))
        contacts = ContactUsers.query.where(
            ContactUsers.organization_id == getOrg(get_jwt()),
        )
        return jsonify([x.id for x in contacts]), 200
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


# Api to get list of Contacts,Segments,Households,Companies,Tags ID's created Between two Dates
@globalendpoints.route("/filter/date/<tab_name>", methods=["GET"])
@user_required()
def date_filter(tab_name):
    start_date = request.args.get("date1")
    end_date = request.args.get("date2")
    s_date, e_date = parser.parse(start_date), parser.parse(end_date)
    tab_mapper = {
        "eblasts": Eblasts,
        "contacts": ContactUsers,
        "segments": SegmentUsers,
        "households": HouseholdUsers,
        "companies": CompanyUsers,
        "tags": TagUsers,
        "pledges": Pledges,
        "forms": Forms,
        "donations": TransactionDonation,
    }
    try:
        for mapper in tab_mapper.keys():
            if mapper == tab_name:
                table = tab_mapper[mapper]
                filtered_data = (
                    db.session.query(table)
                    .filter(table.organization_id == getOrg(get_jwt()))
                    .filter(table.created_on.between(s_date, e_date))
                )
                primary_id = list(table.__table__.primary_key)[0].name
                return jsonify([getattr(x, primary_id) for x in filtered_data]), 200
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


@globalendpoints.route("/export_contacts", methods=["GET"])
@user_required()
def contact_exporter():
    format_type = request.json.get("format")
    fields_to_export = request.json.get("fields")
    export_type = request.json.get("export_type")
    contacts = ContactUsers.query.where(
        ContactUsers.organization_id == getOrg(get_jwt())
    ).all()
    # converting json data to DataFrame object
    df = pd.DataFrame.from_dict(multi_dict_resp(contacts))
    # creating a output Byte stream to write dataframe to a excel file instead of storing it
    buffer = io.BytesIO()
    if format_type == "excel":
        try:
            """
            # specifying the MIME Type for xlsx file types
            """
            XLSX_MIMETYPE = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # converting dataframe to excel file and writing to output buffer
            print(df.columns.values)
            df.to_excel(
                buffer,
                columns=fields_to_export
                if not export_type == "all"
                else df.columns.values,
                encoding="utf-8",
            )
            # Completed Convertion ? Grab starting position from buffer >> return the excel file
            buffer.seek(0)
            filename = "contacts_" + datetime.now().strftime("%Y_%m_%d_%H_%M") + ".xlsx"
            # using send_file to send xlsx file as attachment
            return send_file(
                buffer,
                attachment_filename=filename,
                as_attachment=True,
                mimetype=XLSX_MIMETYPE,
            )
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()

    elif format_type == "csv":
        try:
            df.to_csv(
                buffer,
                columns=fields_to_export
                if not export_type == "all"
                else df.columns.values,
                encoding="utf-8",
                index=False,
            )
            buffer.seek(0)
            filename = "contacts_" + datetime.now().strftime("%Y_%m_%d_%H_%M") + ".csv"
            return send_file(
                buffer,
                attachment_filename=filename,
                as_attachment=True,
                mimetype="text/csv",
            )

        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    else:
        resp = DataResponse(False, "Specify a Format type to export : [csv/excel]")
        return resp.status()


"""
parameter: table_name 
returns:
 keys : [object_fields , object_names ]
 values: [{field_name,field_type},table_name] 
"""


@globalendpoints.route("/fetch/columns/<table_name>", methods=["GET"])
@user_required()
def fetch_columns(table_name):
    try:
        ignore_tables = ["AccessTokenBlocklist", "alembic_version"]
        if engine.has_table(table_name) and table_name not in ignore_tables:
            fields = [
                {"field_name": column.name, "field_type": column.type}
                for column in inspect(db.metadata.tables[table_name]).c
            ]
            normalized_fields = normalize_db_fields(fields)
            field_template = {
                "object_name": table_name,
                "object_fields": normalized_fields,
            }
            return jsonify(field_template), 200
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@globalendpoints.route("/fetch/table_names", methods=["GET"])
@user_required()
def fetch_tables():
    try:
        ignore_tables = ["AccessTokenBlocklist", "alembic_version"]
        tables = [
            {"table_name": table_name}
            for table_name in engine.table_names()
            if table_name not in ignore_tables
        ]
        return jsonify(tables), 200
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()
