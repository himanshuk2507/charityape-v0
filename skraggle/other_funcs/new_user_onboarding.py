import os
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from skraggle.base_helpers.csv_to_dict import csv_to_dict
from skraggle.base_helpers.responser import DataResponse
from skraggle.config import db
from skraggle.contact.models import ContactUsers
from skraggle.config import upload_dir

newuseronboard = Blueprint("newuseronboard", __name__, template_folder="templates")


@newuseronboard.route("/import", methods=["POST"])
def import_users():
    csv_file = request.files["contacts"]
    filename = secure_filename(csv_file.filename)
    csv_file.save(os.path.join(upload_dir, filename))
    if csv_file:
        with open(os.path.join(upload_dir, filename), "r") as f:
            data_list = csv_to_dict(f)
            plain_data = []
            try:
                for data in data_list:
                    data_obj = ContactUsers(**data)
                    plain_data.append(data_obj)
                db.session.add_all(plain_data)
                db.session.commit()
                resp = DataResponse(True, "Contacts Imported Successfully")
                return resp.status()
            except Exception as e:
                resp = DataResponse(False, str(e)[:105])
                return resp.status()
    else:
        resp = DataResponse(False, "Please Import a CSV File")
        return resp.status()
