import django_tables2 as tables
from django_tables2.utils import Accessor

from nautobot.dcim.tables.template_code import CABLE_TERMINATION_PARENT
from nautobot.apps.tables import BaseTable, ColorColumn, ToggleColumn

from .models import CableInventoryItem, MeasurementLog

CABLE_LENGTH = """
{% if record.length %}{{ record.length }} {{ record.get_length_unit_display }}{% else %}&mdash;{% endif %}
"""


class CableInventoryItemTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_cable_utils:cableinventoryitem",
        args=[tables.A("pk")],
        verbose_name="Cable Number",
    )
    type = tables.Column()
    length = tables.TemplateColumn(
        template_code=CABLE_LENGTH,
    )
    color = ColorColumn()
    in_use = tables.TemplateColumn(
        template_code="<span>{% if record.cable %}✔{% else %}✘{% endif %}</span>",
        order_by="cable",
    )

    class Meta(BaseTable.Meta):
        model = CableInventoryItem
        fields = (
            "pk",
            "name",
            "label",
            "owner",
            "type",
            "plug",
            "supplier",
            "storage_rack",
            "procurement_ident",
            "length",
            "color",
            "in_use",
        )
        default_columns = (
            "pk",
            "name",
            "label",
            "owner",
            "type",
            "plug",
            "supplier",
            "storage_rack",
            "procurement_ident",
            "length",
            "color",
            "in_use",
        )


class MeasurementLogTable(BaseTable):
    pk = ToggleColumn()
    link = tables.LinkColumn(
        "plugins:nautobot_cable_utils:measurement_log_edit",
        args=[tables.A("pk")],
    )
    cable = tables.LinkColumn("dcim:cable", args=[tables.A("pk")])

    class Meta(BaseTable.Meta):
        model = MeasurementLog
        fields = ("pk", "link", "cable")
        default_columns = ("pk", "link", "cable")


class NeededCableTable(tables.Table):
    class Meta:
        attrs = {
            "class": "table table-hover table-headings",
        }

    termination_a_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor("termination_a"),
        orderable=False,
        verbose_name="Side A",
    )
    termination_a = tables.LinkColumn(
        accessor=Accessor("termination_a"),
        orderable=False,
        verbose_name="Termination A",
    )
    termination_b_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor("termination_b"),
        orderable=False,
        verbose_name="Side B",
    )
    termination_b = tables.LinkColumn(
        accessor=Accessor("termination_b"),
        orderable=False,
        verbose_name="Termination B",
    )
