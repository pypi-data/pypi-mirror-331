from nautobot.dcim.api.serializers import CableSerializer, ManufacturerSerializer
from nautobot.tenancy.api.serializers import TenantSerializer
from rest_framework.serializers import ModelSerializer

from nautobot.apps.api import BaseModelSerializer, CustomFieldModelSerializerMixin
from rest_framework import serializers

from nautobot_cable_utils.models import CableInventoryItem, CablePlug


class NestedCablePlugSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cable_utils-api:cableplug-detail"
    )

    class Meta:
        model = CablePlug
        fields = ["id", "url", "name"]


class CablePlugSerializer(ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cable_utils-api:cableplug-detail"
    )

    class Meta:
        model = CablePlug
        fields = [
            "id",
            "url",
            "name",
        ]


class CableInventoryItemSerializer(
    CustomFieldModelSerializerMixin, BaseModelSerializer
):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cable_utils-api:cableinventoryitem-detail"
    )
    owner = TenantSerializer()
    cable = CableSerializer()
    plug = CablePlugSerializer()
    supplier = ManufacturerSerializer()

    class Meta:
        model = CableInventoryItem
        fields = [
            "id",
            "url",
            "name",
            "label",
            "type",
            "plug",
            "color",
            "supplier",
            "procurement_ident",
            "length",
            "length_unit",
            "cable",
            "owner",
        ]
