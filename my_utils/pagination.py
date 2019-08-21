
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.serializer_helpers import ReturnDict

from my_utils.utils import my_response_page_data


class BasePagination(PageNumberPagination):
    """
    数据分页类
    """
    page_size = 10
    page_size_query_param = 'page_size'
    page_size_query_description = '每页返回条目数, 不传默认返回10条, 最大返回数50'
    page_query_param = 'page'
    page_query_description = '页码'
    max_page_size = 50

    def get_paginated_response(self, data):
        if isinstance(data, ReturnDict):
            list = []
            list.append(data)
            data = list

        return Response(my_response_page_data(count=self.page.paginator.count,
                                              next=self.get_next_link(),
                                              previous=self.get_previous_link(),
                                              data=data, status='success', msg='获取成功'))