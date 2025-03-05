from . import serializers, filters
from nautobot.apps.api import APIRootView, ModelViewSet
from ..models import CableInventoryItem, CablePlug


class SFPInventoryRootView(APIRootView):

    def get_view_name(self):
        return "SFP Inventory"


class CableInventoryItemViewSet(ModelViewSet):
    queryset = CableInventoryItem.objects.all()
    serializer_class = serializers.CableInventoryItemSerializer
    filterset_class = filters.CableInventoryItemFilterSet


class CablePlugViewSet(ModelViewSet):
    queryset = CablePlug.objects.all()
    serializer_class = serializers.CablePlugSerializer
    filterset_class = filters.CablePlugFilterSet
