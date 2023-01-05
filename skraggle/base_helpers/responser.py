from flask import jsonify

"""
# Return Success/Error Template

# Usage: 
>> from validators_logics.responser import DataResponse

>> response = DataResponse(True or False, 'Message to be displayed')
>> return response.status()

**Returns HttpResponse Status 200 if success is True or 404 if success is False*
"""


class DataResponse:
    def __init__(self, success: bool, message: str, failure_status_code=406):
        self.success = success
        self.message = message
        self.failure_status_code = 404 if not failure_status_code else failure_status_code

    def status(self):
        data_resp = {
            "success": self.success,
            "message": self.message,
        }
        if self.success:
            return jsonify(data_resp), 200
        else:
            return jsonify(data_resp), self.failure_status_code
