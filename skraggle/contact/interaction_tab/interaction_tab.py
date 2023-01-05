from datetime import datetime
from uuid import UUID

from flask import Blueprint, jsonify, request

from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.base_helpers.responser import DataResponse
from skraggle.config import db
from skraggle.contact.models import Interactions, ContactTodo
interactiontab = Blueprint("interactiontab", __name__)


@interactiontab.route("/add", methods=["POST"])
def add_interaction():
    interaction_data = {
        "contact": request.form["contact"],
        "interaction_type": request.form["interaction_type"],
        "date": request.form.get("date", datetime.now()),
        "desc": request.form.get("description", None),
        "attachments": request.form.get("attachments"),
        "subject": request.form["subject"],
        "has_todo": bool(request.form.get("has_todo", False)),
    }
    try:
        add_interaction = Interactions(**interaction_data)
        db.session.add(add_interaction)
        db.session.flush()
        if interaction_data["has_todo"]:
            try:
                todo_data = {
                    "todo": request.form["todo"],
                    "due_date": request.form["due_date"],
                    "assignee": request.form.get("assignee"),
                    "details": request.form.get("details")
                }
                add_todo = ContactTodo(**todo_data)
                add_interaction.todo.append(add_todo)
                db.session.flush()
                if "attachments" in request.form:
                    add_todo.attachments = request.form["attachment"]
            except Exception as e:
                resp = DataResponse(False, str(e))
                return resp.status()
        db.session.commit()
        resp = DataResponse(True, "Interaction Added Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


@interactiontab.route("/<interaction_id>", methods=["GET"])
def list_interaction(interaction_id):
    interaction = Interactions.query.filter_by(interaction_id=interaction_id).first()
    if interaction:
        todo = interaction.todo
        todo_data = dict_resp(todo[0])
        interaction_data = dict_resp(interaction)
        interaction_data["todo"] = [todo_data]
        return jsonify(interaction_data), 200
    else:
        resp = DataResponse(False, "Interaction does not exist with the given ID")
        return resp.status()


@interactiontab.route("/all/<int:page_number>", methods=["GET"])
def all_interaction(page_number):
    instance = Interactions
    order_by_column = "interaction_id"
    api_path = "interactions/all"
    return paginator(page_number, instance, order_by_column, api_path)


@interactiontab.route("/delete", methods=["DELETE"])
def delete_interaction():
    interaction_id = request.args.get("interaction_id")
    print(interaction_id)
    interaction = Interactions.query.filter_by(interaction_id=UUID(interaction_id)).first()
    if interaction:
        db.session.delete(interaction)
        db.session.commit()
        resp = DataResponse(True, "Interaction Deleted Successfully")
        return resp.status()
    else:
        resp = DataResponse(False, "Interaction does not exist with the given ID")
        return resp.status()


