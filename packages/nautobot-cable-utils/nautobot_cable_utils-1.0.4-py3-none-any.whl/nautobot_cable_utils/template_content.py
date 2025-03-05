from nautobot.apps.ui import TemplateExtension

from .models import MeasurementLog
from .models import CableInventoryItem


class CableCommission(TemplateExtension):
    model = "dcim.cable"

    def buttons(self):
        cable = self.context["object"]
        log = None

        maybe_log = MeasurementLog.objects.filter(cable=cable)
        if maybe_log.exists():
            log = maybe_log.first().link

        cable_inventory_item = CableInventoryItem.objects.filter(cable=cable)

        return self.render(
            "nautobot_cable_utils/inc/buttons.html",
            {
                "cable": cable,
                "cable_planned": cable.status.name == "Planned",
                "cable_inventory": cable_inventory_item.exists(),
                "log": log,
            },
        )


class DeviceBulkConnect(TemplateExtension):
    model = "dcim.device"

    def buttons(self):
        device = self.context["object"]
        cable_available = None

        if device.get_cables().filter(status__name="Planned").count() > 0:
            cable_available = (
                device.get_cables().filter(status__name="Planned").first().pk
            )

        return self.render(
            "nautobot_cable_utils/inc/buttons_device.html",
            {
                "device": device,
                "cable_planned": cable_available is not None,
            },
        )


class InterfaceAutoRouteStart(TemplateExtension):
    model = "dcim.interface"

    def buttons(self):
        return self.render(
            "nautobot_cable_utils/inc/buttons_interface.html",
        )


class FrontPortAutoRouteStart(TemplateExtension):
    model = "dcim.frontport"

    def buttons(self):
        return self.render(
            "nautobot_cable_utils/inc/buttons_frontport.html",
        )


class CableInventoryItemPanel(TemplateExtension):
    model = "dcim.cable"

    def right_page(self):
        return self.render("nautobot_cable_utils/inc/cableinventoryitem_panel.html")


template_extensions = [
    CableCommission,
    DeviceBulkConnect,
    InterfaceAutoRouteStart,
    FrontPortAutoRouteStart,
    CableInventoryItemPanel,
]
