from rest_framework import filters as drf_filter
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.record.models import PushRecord


class PushFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    start_time = filters.DateTimeFilter(method='start_time_filter', label='开始时间', help_text='开始时间')
    end_time = filters.DateTimeFilter(method='end_time_filter', label='结束时间', help_text='结束时间')

    def start_time_filter(self, queryset, name, value):
        return queryset.filter(create_time__gte=value)

    def end_time_filter(self, queryset, name, value):
        return queryset.filter(create_time__lte=value)

    class Meta:
        model = PushRecord
        fields = ['start_time', 'end_time']
