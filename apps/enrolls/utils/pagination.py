from rest_framework import pagination

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 1000