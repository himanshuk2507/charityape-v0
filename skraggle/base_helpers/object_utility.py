from datetime import datetime
from simple_salesforce import SalesforceMalformedRequest
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.config import db, engine
from skraggle.contact.models import ContactUsers
from skraggle.campaigns.models import Campaigns
from skraggle.donation.models import ScheduleRecurringDonation, TransactionDonation, Pledges
from skraggle.forms.models import Forms


core_tables = {
    "ContactUsers": ContactUsers,
    "Campaigns": Campaigns,
    "ScheduleRecurringDonation": ScheduleRecurringDonation,
    "Pledges": Pledges,
    "Forms": Forms,
    "TransactionDonation": TransactionDonation,
}


class ObjectHandler:
    def __init__(
        self, table_name, organization_id, sobject="",
    ):

        self.table_name = table_name
        self.organization_id = organization_id
        if sobject != "":
            self.sobject = sobject
        if table_name in core_tables.keys():
            self.table = core_tables[table_name]

    def make(self):
        if self.table_name in core_tables.keys():
            table = core_tables[self.table_name]
            fields = get_fields(table, ignore=False)
            foo_object = dict.fromkeys(fields)
            created = ["joined_on", "created", "created_on", "joined"]
            foo_object.update({"organization_id": self.organization_id})
            for made in created:
                if made in foo_object.keys():
                    foo_object.update({made: datetime.now()})
            return foo_object
        else:
            return False

    def get_skraggle_records(self, connection, fields_to_dump, object_to_dump):
        preserve_field_mappings = {
            fields_to_dump[key][object_to_dump]: key for key in fields_to_dump.keys()
        }
        fields_for_unique_object = list(
            set(
                [
                    fields_to_dump[field][object_to_dump]
                    for field in fields_to_dump.keys()
                    if list(fields_to_dump[field].keys())[0] == object_to_dump
                ]
            )
        )
        try:
            query = (
                f'SELECT {",".join(fields_for_unique_object)} from "{object_to_dump}"'
            )

            records_obj = connection.execute(query)
            records_list = list(
                [x[key] for key in fields_for_unique_object] for x in records_obj
            )
            records = [
                {
                    preserve_field_mappings[k]: v
                    for (k, v) in zip(fields_for_unique_object, x)
                }
                for x in records_list
            ]
            return {
                "message": records,
                "success": True,
                "records_synced": len("records"),
            }
        except SalesforceMalformedRequest as e:
            return {
                "message": "Invalid Mapping Rules or Field Names",
                "success": False,
            }
        except Exception as e:
            return {"message": str(e)[:105], "success": False}

    def get_salesforce_records(self, connection, fields_to_fetch, object_to_fetch):
        global data
        preserve_field_mappings = {
            fields_to_fetch[key][object_to_fetch]: key for key in fields_to_fetch.keys()
        }
        fields_for_unique_object = list(
            set(
                [
                    fields_to_fetch[field][object_to_fetch]
                    for field in fields_to_fetch.keys()
                    if list(fields_to_fetch[field].keys())[0] == object_to_fetch
                ]
            )
        )
        try:
            query = (
                f"SELECT {','.join(fields_for_unique_object)} from {object_to_fetch}"
            )
            contacts = connection.query_all(query)
            data = list(
                [x[key] for key in fields_for_unique_object]
                for x in contacts["records"]
            )
            records = [
                {
                    preserve_field_mappings[k]: v
                    for (k, v) in zip(fields_for_unique_object, x)
                }
                for x in data
            ]
            return {
                "message": records,
                "success": True,
                "records_synced": len(records),
            }
        except SalesforceMalformedRequest as e:
            return {
                "message": "Invalid Mapping Rules or Field Names",
                "success": False,
            }
        except Exception as e:
            return {"message": str(e)[:105], "success": False}

    def get_unique_objects(
        self,
        fields_to_fetch,
        skraggle_fields_to_map,
        salesforce_fields_to_map,
        fields_to_dump,
    ):
        unique_objects = {"salesforce": None, "Skraggle": None}
        if list(fields_to_fetch.keys()) == skraggle_fields_to_map:

            salesforce_unique_objects_to_fetch = list(
                set(
                    [
                        list(fields_to_fetch[obj].keys())[0]
                        for obj in fields_to_fetch.keys()
                    ]
                )
            )
            unique_objects["salesforce"] = salesforce_unique_objects_to_fetch
        if list(fields_to_dump.keys()) == salesforce_fields_to_map:
            skraggle_unique_objects_to_fetch = list(
                set(
                    [
                        list(fields_to_dump[obj].keys())[0]
                        for obj in fields_to_dump.keys()
                    ]
                )
            )
            unique_objects["skraggle"] = skraggle_unique_objects_to_fetch
        return unique_objects

    def process(
        self,
        connection,
        fields_to_fetch,
        skraggle_fields_to_map,
        salesforce_fields_to_map,
        fields_to_dump,
        sync_type,
    ):
        unique_objects = self.get_unique_objects(
            fields_to_fetch,
            skraggle_fields_to_map,
            salesforce_fields_to_map,
            fields_to_dump,
        )
        if sync_type == "import":
            for _unique_object in unique_objects["salesforce"]:
                return self.get_salesforce_records(
                    connection, fields_to_fetch, _unique_object
                )
        elif sync_type == "export":
            for _unique_object in unique_objects["skraggle"]:
                connection = engine
                return self.get_skraggle_records(
                    connection, fields_to_dump, _unique_object
                )

    def import_records(self, records):
        for record in records:
            foo_object = self.make()
            foo_object.update(record)
            table = self.table
            try:
                new_record = table(**foo_object)
                db.session.add(new_record)
                db.session.commit()
            except Exception as e:
                resp = {"message": str(e)[:105], "success": False}
                return resp
        resp = {"message": "Sync Successfull", "success": True}
        return resp

    def export_records(self, records, connection):
        for record in records:
            foo_object = self.make()
            foo_object.update(record)
            sobject = self.sobject
            sobject_type = getattr(connection, sobject).metadata()['objectDescribe']["custom"]
            try:
                getattr(connection, sobject).create(record)
            except Exception as e:
                resp = {"message": str(e)[:105], "success": False}
                return resp
        resp = {"message": "Sync Successfull", "success": True}
        return resp
