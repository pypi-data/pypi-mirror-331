import django_filters
from django.db.models import Q

from nautobot.dcim.models import Manufacturer, Rack
from nautobot.apps.filters import BaseFilterSet, NaturalKeyOrPKMultipleChoiceFilter
from nautobot.tenancy.models import Tenant

from .models import CableInventoryItem, CablePlug


class CableInventoryItemFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    owner = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label="Owner",
    )
    plug = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=CablePlug.objects.all(),
        label="Plug",
    )

    supplier = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label="Supplier",
    )

    storage_rack = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        label="Storage Rack",
    )
    in_use = django_filters.BooleanFilter(method="in_use_filter", label="In use")

    class Meta:
        model = CableInventoryItem
        fields = ["name", "type", "color", "procurement_ident", "length", "length_unit"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(label__icontains=value)
            | Q(procurement_ident__icontains=value)
        )
        return queryset.filter(qs_filter)

    def in_use_filter(self, queryset, name, value):
        if value:
            return queryset.exclude(cable=None)
        else:
            return queryset.filter(cable=None)
