from flask import jsonify
from skraggle.constants import DEFAULT_PAGE_SIZE


def paginated_response(page_number, total_records, data, previous_page, next_page):
    if total_records <= DEFAULT_PAGE_SIZE:
        return jsonify({
            "message": data,
            "success": True
        })

    if (page_number * DEFAULT_PAGE_SIZE) >= total_records:
        return jsonify({
            "message": data,
            "success": True,
            "previous_page": previous_page,
        })

    if page_number > 1:
        return jsonify({
            "message": data,
            "success": True,
            "next_page": next_page,
            "previous_page": previous_page,
        })

    else:
        return jsonify({
            "message": data,
            "success": True,
            "next_page": next_page,
        })
