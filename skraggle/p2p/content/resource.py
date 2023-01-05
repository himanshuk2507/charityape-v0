from flask import request, Blueprint, jsonify
from skraggle.p2p.models import Resource, db

resourceviews = Blueprint("resourceviews", __name__)


@resourceviews.route('/create', methods=["POST"])
def add_resource():
    file = request.form["file"]
    title = request.form["title"]
    categories = request.form["category"]
    category = categories
    resource = Resource(file=file, title=title, category=category)
    db.session.add(resource)
    db.session.commit()
    data = {
        "message": f" Resource with Title: {resource.title} was added successfully",
        "success": True}
    return jsonify(data), 200


@resourceviews.route('/update', methods=["PATCH"])
def update_resource():
    resource_id = request.args.get('id')
    resource = Resource.query.filter_by(id=resource_id).one_or_none()
    if not resource:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    file = request.form["file"]
    title = request.form["title"]
    categories = request.form["category"]
    resource.file = file
    resource.title = title
    resource.category = categories
    Resource(file=file, title=title, category=categories)
    db.session.commit()
    data = {
        "message": f" Resource with Title: {resource.title} was updated successfully",
        "success": True}
    return jsonify(data), 200


@resourceviews.route('/all')
def all_resource():
    resource = Resource.query.all()
    return {"Resource_list": [str(x.id) for x in resource]}


@resourceviews.route('/info/<resource_id>')
def info_resource(resource_id):
    resource = Resource.query.filter_by(id=resource_id).one_or_none()
    if not resource:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = resource.to_dict()
    return jsonify(data), 200


@resourceviews.route('/delete', methods=["DELETE"])
def delete_resource():
    resource_id = request.args.get('id')
    try:
        resource = Resource.query.filter_by(id=resource_id).delete()
        db.session.commit()
        data = {"message": f" ID: {resource_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400