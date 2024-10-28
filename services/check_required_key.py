from services.responses import bad_request_response

def check_required_key(request, key, custom_message=None):
    if key not in request.data:
        error_message = custom_message or f"{key} key is missing in the request data"
        return bad_request_response(error_message)
    return None