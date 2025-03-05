from nautobot.apps.ui import (
    ButtonColorChoices,
    NavMenuTab,
    NavMenuGroup,
    NavMenuItem,
    NavMenuButton,
)


menu_items = (
    NavMenuTab(
        name="Plugins",
        groups=[
            NavMenuGroup(
                name="Cable Utilities",
                items=[
                    NavMenuItem(
                        link="plugins:nautobot_cable_utils:cableinventoryitem_list",
                        name="Cable Inventory",
                        permissions=["dcim.view_cables"],
                        buttons=[
                            NavMenuButton(
                                link="plugins:nautobot_cable_utils:cableinventoryitem_add",
                                title="Add Cable Inventory Item",
                                icon_class="mdi mdi-plus-thick",
                                button_class=ButtonColorChoices.GREEN,
                            ),
                            NavMenuButton(
                                link="plugins:nautobot_cable_utils:cableinventoryitem_import",
                                title="Import Cable Inventory Items",
                                icon_class="mdi mdi-database-import-outline",
                                button_class=ButtonColorChoices.BLUE,
                            ),
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cable_utils:measurement_log_list",
                        name="Measurement Logs",
                        permissions=["dcim.view_cables"],
                        buttons=[
                            NavMenuButton(
                                link="plugins:nautobot_cable_utils:measurement_log_add",
                                title="Add Measurement Log",
                                icon_class="mdi mdi-plus-thick",
                                button_class=ButtonColorChoices.GREEN,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
)
