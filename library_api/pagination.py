from collections import OrderedDict

from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NoCountPaginator(Paginator):
    @property
    def count(self):
        return 9999999

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page + 1
        page_items = list(self.object_list[bottom:top])
        self._has_next = len(page_items) > self.per_page
        items = page_items[: self.per_page]
        return self._get_page(items, number, self)


class NoCountPagination(PageNumberPagination):
    django_paginator_class = NoCountPaginator

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
