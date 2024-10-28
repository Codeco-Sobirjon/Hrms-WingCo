from django.http import JsonResponse
from rest_framework import status


class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response is None:
            return self.handle_404(request)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return self.handle_404(request)

        return response

    def handle_404(self, request):
        data = {'detail': 'Page Not found'}
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)