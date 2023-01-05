from flask import Blueprint, render_template, request, redirect, jsonify
from flask_jwt_extended import get_jwt

from skraggle.contact.models import ContactUsers, ContactTodo
from skraggle.config import db
import uuid
import os
from werkzeug.utils import secure_filename
from skraggle.config import upload_dir, allowed_file
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg

todotab = Blueprint("todotab", __name__)


@todotab.route("/create", methods=["GET", "POST"])
@user_required()
def todo_add():
    id = request.args.get("id")
    contact = ContactUsers.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).first()
    resp = {"Data": "", "attachment": "NA"}
    if request.method == "POST":
        if contact:
            todo = request.form["todo"]
            due_date = request.form["due_date"]
            details = request.form.get("details", None)
            assignee = request.form.get("assignee", None)
            todo = ContactTodo(todo=todo, due_date=due_date,details = details,assignee=assignee)
            contact.todo_id.append(todo)
            resp["Data"] = "Todo Created"
            if "attachment" in request.files:
                file = request.files["attachment"]
                if file.filename == "":
                    resp["attachment"] = "No file selected for uploading"

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    fileext = os.path.splitext(filename)
                    print(fileext)
                    todo_current = ContactTodo.query.order_by(-ContactTodo.id).first()
                    filename = str(uuid.uuid4()) + fileext[-1]

                    file.save(os.path.join(upload_dir, filename))

                    todo_current.attachments = "{}\{}".format(upload_dir, filename)
                    todo_current.attachments_name = filename

                    resp["attachment"] = "attachment uploaded succesfully"
                else:
                    resp["attachment"] = "Filetype not Allowed"

            db.session.flush()
            todo.organization_id = getOrg(get_jwt())
            db.session.commit()

        else:
            resp["Data"] = "Todo Does not Exist"
    return jsonify(resp)


@todotab.route("/<uuid:id>")
@user_required()
def todo_list(id):
    contact = ContactUsers.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).first()
    if contact:
        todos = contact.todo_id
        data = {
            "todos": [
                [todo.todo, todo.due_date, todo.id, todo.completed] for todo in todos
            ]
        }
    else:
        data = {"Error": "Contact does not exist"}
    return jsonify(data)


@todotab.route("/delete")
@user_required()
def todo_delete():
    id = request.args.get("id")
    todo = ContactTodo.query.filter_by(id=id, organization_id=getOrg(get_jwt())).first()
    if todo:
        ContactTodo.query.filter_by(id=id, organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = "Deleted"
    else:
        data = "Does not Exist"
    return jsonify(data)


@todotab.route("/status")
@user_required()
def todo_status():
    id = request.args.get("id")
    status = request.args.get("status")
    todo_task = ContactTodo.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).first()
    print(todo_task)
    data = "Invalid Parameters, Accepts : true , false"
    if status.lower() == "true":
        todo_task.completed = True
        data = f"task marked as {status.lower()}"
    elif status.lower() == "false":
        todo_task.completed = False
        data = f"task marked as {status.lower()}"
    db.session.commit()

    return jsonify(data)
