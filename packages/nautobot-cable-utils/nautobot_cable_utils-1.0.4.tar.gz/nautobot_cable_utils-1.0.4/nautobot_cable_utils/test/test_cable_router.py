from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from nautobot.extras.models import Status
from nautobot.dcim.choices import CableTypeChoices, InterfaceTypeChoices
from nautobot.dcim.models import (
    Location,
    LocationType,
    Manufacturer,
    DeviceType,
    Device,
    Rack,
    RearPortTemplate,
    Cable,
    RearPort,
    InterfaceTemplate,
    FrontPortTemplate,
)
from nautobot.extras.models import Role
from nautobot_cable_utils.cable_router import CableRouter


class CableRouterTest(TestCase):

    @classmethod
    def _populate_locations(cls):

        location_type = LocationType.objects.create(name="Site")
        status = Status.objects.get(name="Active")
        location = Location.objects.create(
            name="1519 - RZGö", location_type=location_type, status=status
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1")
        dt_pp = DeviceType.objects.create(
            manufacturer=manufacturer, model="Patch Panel"
        )

        rpt = RearPortTemplate.objects.create(device_type=dt_pp, name="1/1")

        FrontPortTemplate.objects.create(
            device_type=dt_pp,
            name="1/1",
            rear_port_template=rpt,
        )

        dt_d = DeviceType.objects.create(manufacturer=manufacturer, model="Device")

        InterfaceTemplate.objects.create(
            device_type=dt_d,
            name="swp1",
            type=InterfaceTypeChoices.TYPE_100GE_QSFP28,
        )
        device_content_type = ContentType.objects.get_for_model(Device)
        role = Role.objects.create(name="Device Role 1")
        role.content_types.set([device_content_type])

        return location, manufacturer, dt_pp, dt_d, role

    @classmethod
    def _populate_edges(
        cls, location, dt_pp, dt_d, role, edges, device_locations, cable_type_choice
    ):

        rack_names = set([x for e in edges for x in e])
        status = Status.objects.get(name="Active")
        for rack_name in rack_names:
            Rack.objects.create(
                name=rack_name,
                location=location,
                status=status,
            )

        patched_cables = list()

        for edge in edges:
            (rack_a, rack_b) = edge

            device_a = Device.objects.create(
                role=role,
                device_type=dt_pp,
                location=location,
                rack=Rack.objects.get(location=location, name=rack_a),
                status=status,
            )

            device_b = Device.objects.create(
                role=role,
                device_type=dt_pp,
                location=location,
                rack=Rack.objects.get(location=location, name=rack_b),
                status=status,
            )

            c = Cable.objects.create(
                termination_a=RearPort.objects.get(device=device_a),
                termination_b=RearPort.objects.get(device=device_b),
                type=cable_type_choice,
                status=status,
            )

            patched_cables.append(c)

        start_dev = Device.objects.create(
            role=role,
            device_type=dt_d,
            location=location,
            rack=Rack.objects.get(location=location, name=device_locations[0]),
            status=status,
        )

        end_dev = Device.objects.create(
            role=role,
            device_type=dt_d,
            location=location,
            rack=Rack.objects.get(location=location, name=device_locations[1]),
            status=status,
        )

        return patched_cables, start_dev, end_dev

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        location, manufacturer, dt_pp, dt_d, role = cls._populate_locations()
        cls.simple_patch_cables, cls.simple_patch_start, cls.simple_patch_end = (
            cls._populate_edges(
                location,
                dt_pp,
                dt_d,
                role,
                [
                    ("1519-B-1009", "1519-B-1010"),
                    ("1519-B-1011", "1519-B-1012"),
                    ("1519-B-1010", "1519-B-1011"),
                ],
                [
                    "1519-B-1009",
                    "1519-B-1012",
                ],
                CableTypeChoices.TYPE_SMF,
            )
        )

        (
            cls.neighbour_patch_cables,
            cls.neighbour_patch_start,
            cls.neighbour_patch_end,
        ) = cls._populate_edges(
            location,
            dt_pp,
            dt_d,
            role,
            [
                ("1519-A-1009", "1519-A-1010"),
            ],
            [
                "1519-A-1009",
                "1519-A-1010",
            ],
            CableTypeChoices.TYPE_SMF,
        )

        cls.rack_hop_cables, cls.rack_hop_start, cls.rack_hop_end = cls._populate_edges(
            location,
            dt_pp,
            dt_d,
            role,
            [
                ("1519-C-1009", "1519-C-1010"),
                ("1519-C-1011", "1519-C-1012"),
            ],
            [
                "1519-C-1009",
                "1519-C-1012",
            ],
            CableTypeChoices.TYPE_SMF,
        )

    def test_dummy(self):

        content_type = ContentType.objects.get(app_label="dcim", model="interface")
        cr = CableRouter(
            self.simple_patch_start.interfaces.first(),
            content_type,
            self.simple_patch_end.interfaces.first(),
            content_type,
            "fiber_sm",
        )
        cr_reverse = CableRouter(
            self.simple_patch_end.interfaces.first(),
            content_type,
            self.simple_patch_start.interfaces.first(),
            content_type,
            "fiber_sm",
        )
        cr_simple_hop = CableRouter(
            self.neighbour_patch_end.interfaces.first(),
            content_type,
            self.neighbour_patch_start.interfaces.first(),
            content_type,
            "fiber_sm",
            enable_next_rack_hops=True,
        )
        path = cr.get_path()
        path_reverse = cr_reverse.get_path()
        path_simple_hop = cr_simple_hop.get_path()

        self.assertEqual(len(path), 3)
        self.assertEqual(len(path_reverse), 3)
        self.assertEqual(len(path_simple_hop), 1)
        self.assertEqual(
            sorted(map(lambda c: c["cable_id"], path)),
            sorted(map(lambda c: c.id, self.simple_patch_cables)),
        )
        self.assertEqual(
            sorted(map(lambda c: c["cable_id"], path_reverse)),
            sorted(map(lambda c: c.id, self.simple_patch_cables)),
        )

    def test_rack_hop_disabled(self):
        content_type = ContentType.objects.get(app_label="dcim", model="interface")
        cr = CableRouter(
            self.rack_hop_start.interfaces.first(),
            content_type,
            self.rack_hop_end.interfaces.first(),
            content_type,
            "fiber_sm",
        )
        cr_easy_hop = CableRouter(
            self.rack_hop_start.interfaces.first(),
            content_type,
            self.rack_hop_end.interfaces.first(),
            content_type,
            "fiber_sm",
            enable_next_rack_hops=True,
        )
        path = cr.get_path()
        cr_easy_hop_path = cr_easy_hop.get_path()
        self.assertEqual(path, [])
        self.assertEqual(len(cr_easy_hop_path), 2)
