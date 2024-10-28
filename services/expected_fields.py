

def check_expected_fields(request, expected_fields):
    received_fields = set(request.data.keys())
    unexpected_fields = received_fields - expected_fields
    if unexpected_fields:
        return unexpected_fields