from flask import jsonify


def no_result_found_response(key_id):
    return jsonify({
        "success": False,
        "message": f"Key ID: {key_id} doesn't correspond to a valid key record"
    }), 404


def generic_exception_response(e):
    return jsonify({
        "success": False,
        "message": f"Following error occurred while serving the request: {str(e)[:120]}"
    })
