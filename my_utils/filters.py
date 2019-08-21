from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class MySearchFilter(filters.SearchFilter):
    search_description = '查询参数'
