from django import forms
from django.forms import (
    Form,
    ChoiceField,
    CharField,
    IntegerField,
    BooleanField,
    NullBooleanField,
)

from nautobot.circuits.models import Circuit, CircuitTermination, Provider
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from nautobot.dcim.choices import CableTypeChoices, CableLengthUnitChoices
from nautobot.dcim.models import (
    Cable,
    ConsolePort,
    ConsoleServerPort,
    Device,
    FrontPort,
    Interface,
    PowerFeed,
    PowerOutlet,
    PowerPanel,
    PowerPort,
    Rack,
    RearPort,
    Manufacturer,
    Location,
)

from nautobot.extras.models import Status
from nautobot.apps.choices import ChoiceSet

from nautobot.apps.forms import (
    BootstrapMixin,
    ColorSelect,
    CSVModelForm,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    StaticSelect2,
    add_blank_choice,
    parse_alphanumeric_range,
    DynamicModelMultipleChoiceField,
    NautobotFilterForm,
    NautobotBulkEditForm,
)
from nautobot.tenancy.models import Tenant
from .cable_router import CableRouter

from .models import CableInventoryItem, MeasurementLog, CablePlug
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import re

NUMERIC_EXPANSION_PATTERN = r"\[((?:\d+[?:,-])+\d+)\]"


def expand_alphanumeric_pattern(string):
    """
    Expand an alphabetic pattern into a list of strings.
    """
    lead, pattern, remnant = re.split(NUMERIC_EXPANSION_PATTERN, string, maxsplit=1)
    parsed_range = parse_alphanumeric_range(pattern)

    maximum_length = max([len(str(x)) for x in parsed_range])

    for i in parsed_range:
        padded_i = str(i).zfill(maximum_length)
        if re.search(NUMERIC_EXPANSION_PATTERN, remnant):
            for string2 in expand_alphanumeric_pattern(remnant):
                yield f"{lead}{padded_i}{string2}"
        else:
            yield f"{lead}{padded_i}{remnant}"


class ExpandableCableNumberPatternField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = """
                Numeric ranges are supported for bulk creation. Mixed cases and types within a single range
                are not supported. Leading zeros will be added. Examples:
                <ul>
                    <li><code>e[0-3][0-13,17]</code></li>
                </ul>
                """

    def to_python(self, value):
        if not value:
            return ""
        if re.search(NUMERIC_EXPANSION_PATTERN, value):
            return list(expand_alphanumeric_pattern(value))
        return [value]


class ConnectCableToDeviceForm(BootstrapMixin, forms.ModelForm):
    """
    Base form for connecting a Cable to a Device component
    """

    termination_a_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label="Location",
        required=False,
    )
    termination_a_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label="Rack",
        required=False,
        display_field="display_name",
        null_option="None",
        query_params={"location": "$termination_a_location"},
    )
    termination_a_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label="Device",
        required=False,
        display_field="display_name",
        query_params={
            "location": "$termination_a_location",
            "rack": "$termination_a_rack",
        },
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label="Rack",
        required=False,
        display_field="display_name",
        null_option="None",
        query_params={"location": "$termination_b_location"},
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label="Device",
        required=False,
        display_field="display_name",
        query_params={
            "location": "$termination_b_location",
            "rack": "$termination_b_rack",
        },
    )

    class Meta:
        model = Cable
        fields = [
            "termination_a_location",
            "termination_a_rack",
            "termination_a_device",
            "termination_a_id",
            "termination_b_location",
            "termination_b_rack",
            "termination_b_device",
            "termination_b_id",
        ]

    def clean_termination_a_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_a_id"], "pk", None)

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_b_id"], "pk", None)


class ConnectConsolePortToConsoleServerPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectConsolePortToFrontPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectConsolePortToRearPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectConsoleServerPortToFrontPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectConsoleServerPortToRearPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectPowerfeedToPowerPortForm(ConnectCableToDeviceForm):
    termination_a_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label="Location",
        required=False,
        display_field="cid",
    )
    termination_a_powerpanel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        label="Power Panel",
        required=False,
        query_params={
            "location": "$termination_a_location",
        },
    )
    termination_a_id = DynamicModelChoiceField(
        queryset=PowerFeed.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"power_panel_id": "$termination_a_powerpanel"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )

    class Meta:
        model = Cable
        fields = [
            "termination_a_location",
            "termination_a_powerpanel",
            "termination_a_id",
            "termination_b_location",
            "termination_b_rack",
            "termination_b_device",
            "termination_b_id",
        ]


class ConnectPowerOutletToPowerPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectInterfaceForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_a_device",
            "kind": "physical",
        },
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_b_device",
            "kind": "physical",
        },
    )


class ConnectFrontPortToInterfaceForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_b_device",
            "kind": "physical",
        },
    )


class ConnectInterfaceToRearPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_a_device",
            "kind": "physical",
        },
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectCircuitTerminationToInterfaceForm(ConnectCableToDeviceForm):
    termination_a_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(), label="Provider", required=False
    )
    termination_a_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_a_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label="Circuit",
        display_field="cid",
        query_params={
            "provider_id": "$termination_a_provider",
            "location": "$termination_a_location",
        },
    )
    termination_a_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label="Side",
        display_field="term_side",
        disabled_indicator="cable",
        query_params={"circuit_id": "$termination_a_circuit"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_b_device",
            "kind": "physical",
        },
    )

    class Meta:
        model = Cable
        fields = [
            "termination_a_provider",
            "termination_a_location",
            "termination_a_circuit",
            "termination_a_id",
            "termination_b_location",
            "termination_b_rack",
            "termination_b_device",
            "termination_b_id",
        ]


class ConnectCircuitTerminationForm(BootstrapMixin, forms.ModelForm):
    termination_a_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(), label="Provider", required=False
    )
    termination_a_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_a_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label="Circuit",
        display_field="cid",
        query_params={
            "provider_id": "$termination_a_provider",
            "location": "$termination_a_location",
        },
    )
    termination_a_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label="Side",
        display_field="term_side",
        disabled_indicator="cable",
        query_params={"circuit_id": "$termination_a_circuit"},
    )
    termination_b_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(), label="Provider", required=False
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_b_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label="Circuit",
        display_field="cid",
        query_params={
            "provider_id": "$termination_b_provider",
            "location": "$termination_b_location",
        },
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label="Side",
        display_field="term_side",
        disabled_indicator="cable",
        query_params={"circuit_id": "$termination_b_circuit"},
    )

    class Meta:
        model = Cable
        fields = [
            "termination_a_provider",
            "termination_a_location",
            "termination_a_circuit",
            "termination_a_id",
            "termination_b_provider",
            "termination_b_location",
            "termination_b_circuit",
            "termination_b_id",
            "type",
            "status",
            "label",
            "color",
            "length",
            "length_unit",
        ]

    def clean_termination_a_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_a_id"], "pk", None)

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_b_id"], "pk", None)


class ConnectFrontPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectFrontPortToRearPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectRearPortForm(ConnectCableToDeviceForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_a_device"},
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectCircuitTerminationToForm(BootstrapMixin, forms.ModelForm):
    termination_a_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(), label="Provider", required=False
    )
    termination_a_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_a_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label="Circuit",
        display_field="cid",
        query_params={
            "provider_id": "$termination_a_provider",
            "location": "$termination_a_location",
        },
    )
    termination_a_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label="Side",
        display_field="term_side",
        disabled_indicator="cable",
        query_params={"circuit_id": "$termination_a_circuit"},
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label="Rack",
        required=False,
        display_field="display_name",
        null_option="None",
        query_params={"location": "$termination_b_location"},
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label="Device",
        required=False,
        display_field="display_name",
        query_params={
            "location": "$termination_b_location",
            "rack": "$termination_b_rack",
        },
    )

    class Meta:
        model = Cable
        fields = [
            "termination_a_provider",
            "termination_a_location",
            "termination_a_circuit",
            "termination_a_id",
            "termination_b_location",
            "termination_b_rack",
            "termination_b_device",
            "termination_b_id",
        ]

    def clean_termination_a_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_a_id"], "pk", None)

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_b_id"], "pk", None)


class ConnectCircuitTerminationToFrontPortForm(ConnectCircuitTerminationToForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class ConnectCircuitTerminationToRearPortForm(ConnectCircuitTerminationToForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={"device": "$termination_b_device"},
    )


class CableInventoryItemForm(BootstrapMixin, forms.ModelForm):
    name = forms.CharField(label="Cable Number")

    class Meta:
        model = CableInventoryItem
        fields = (
            "name",
            "label",
            "owner",
            "type",
            "plug",
            "supplier",
            "storage_rack",
            "procurement_ident",
            "color",
            "length",
            "length_unit",
        )


class CableInventoryItemBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableCableNumberPatternField(label="Cable Number Pattern")


class CableInventoryItemBulkForm(CableInventoryItemForm):

    def save(self, commit=True):
        if not self.instance.label:
            self.instance.label = self.instance.name

        return super().save(commit)


class CableInventoryItemBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CableInventoryItem.objects.all(), widget=forms.MultipleHiddenInput
    )

    type = forms.ChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        widget=StaticSelect2(),
    )
    color = forms.CharField(max_length=6, required=False, widget=ColorSelect())

    owner = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    plug = DynamicModelChoiceField(
        queryset=CablePlug.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    supplier = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    storage_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    procurement_ident = CharField(
        max_length=100, required=False, label="Procurement Identifier"
    )

    length = IntegerField(
        required=False,
        min_value=0,
    )
    length_unit = forms.ChoiceField(
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False,
        widget=StaticSelect2(),
    )

    class Meta:
        nullable_fields = [
            "type",
            "owner",
            "color",
            "plug",
            "supplier",
            "storage_rack",
            "procurement_ident",
            "length",
            "length_unit",
        ]


class CableInventoryItemFilterForm(NautobotFilterForm):
    model = CableInventoryItem
    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False, label="Cable Number")
    type = forms.MultipleChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        widget=StaticSelect2(),
    )
    color = forms.CharField(max_length=6, required=False, widget=ColorSelect())

    owner = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    plug = DynamicModelMultipleChoiceField(
        queryset=CablePlug.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    supplier = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    storage_rack = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
    )
    procurement_ident = CharField(
        max_length=100, required=False, label="Procurement Identifier"
    )
    length = IntegerField(required=False, label="Length")
    length_unit = forms.MultipleChoiceField(
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False,
        widget=StaticSelect2(),
    )
    in_use = NullBooleanField(
        required=False,
        label="In use",
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )


class CommissionForm(BootstrapMixin, forms.Form):
    cable = forms.ModelChoiceField(
        queryset=Cable.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput(),
    )
    inventory_item = forms.CharField(
        required=False,
    )

    def clean(self):
        super().clean()
        try:
            if (
                CableInventoryItem.objects.get(
                    name=self.cleaned_data["inventory_item"]
                ).cable
                is not None
            ):
                raise forms.ValidationError(
                    {
                        "inventory_item": "the assigned cable inventory_item is already in use"
                    }
                )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                {"inventory_item": "the assigned cable inventory_item does not exist"}
            )

    def save(self):

        inventory_item = CableInventoryItem.objects.get(
            name=self.cleaned_data["inventory_item"]
        )
        cable = self.cleaned_data["cable"]

        for field in ["type", "label", "color", "length", "length_unit"]:
            value = getattr(inventory_item, field)
            if value:
                setattr(cable, field, value)

        if not inventory_item.label:
            cable.label = inventory_item.name

        connected_status = None
        statuses = Status.objects.get_for_model(Cable)

        for status in statuses:
            if status.name == "Connected":
                connected_status = status

        cable.status = connected_status
        cable.save()
        inventory_item.cable = cable
        inventory_item.save()

        return cable


class CableInventoryItemCSVForm(CSVModelForm):
    owner = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned Owner",
    )
    plug = CSVModelChoiceField(
        queryset=CablePlug.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Plug",
    )
    supplier = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Supplier",
    )

    class Meta:
        model = CableInventoryItem
        fields = CableInventoryItem.import_csv_headers


class MeasurementLogForm(BootstrapMixin, forms.ModelForm):
    cable = DynamicModelChoiceField(queryset=Cable.objects.all(), display_field="label")

    class Meta:
        model = MeasurementLog
        fields = ("link", "cable")


class CableRouterMediaChoices(ChoiceSet):
    FIBER_SM = "fiber_sm"
    FIBER_MM = "fiber_mm"
    COPPER = "copper"
    CHOICES = (
        (FIBER_SM, "Single-Mode Fiber"),
        (FIBER_MM, "Multi-Mode Fiber"),
        (COPPER, "Copper"),
    )


class CableRouterLinkForm(BootstrapMixin, Form):
    """
    Base form for connecting a Cable to a Device component
    """

    termination_a_type = None
    termination_b_type = None
    termination_a = None

    def __init__(self, *args, **kwargs):
        self.termination_a = kwargs.pop("termination_a")
        self.termination_a_type = kwargs.pop("termination_a_type")
        self.termination_b_type = kwargs.pop("termination_b_type")
        super().__init__(*args, **kwargs)

    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(), label="Location", required=False
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label="Rack",
        required=False,
        display_field="display_name",
        null_option="None",
        query_params={"location": "$termination_b_location"},
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label="Device",
        required=False,
        display_field="display_name",
        query_params={
            "location": "$termination_b_location",
            "rack": "$termination_b_rack",
        },
    )

    media_type = ChoiceField(choices=CableRouterMediaChoices, label="Media Type")

    allow_next_rack_hops = BooleanField(
        label="Allow Next Rack Patches", initial=True, required=False
    )

    class Meta:
        fields = [
            "termination_a_location",
            "termination_a_rack",
            "termination_a_device",
            "termination_a_id",
            "termination_b_location",
            "termination_b_rack",
            "termination_b_device",
            "termination_b_id",
        ]

    def clean(self):
        cleaned_data = super().clean()

        termination_b_model = self.termination_b_type.model_class()
        termination_b = termination_b_model.objects.get(
            id=cleaned_data["termination_b_id"]
        )
        media_type = self.cleaned_data["media_type"]

        cleaned_data["cable_router"] = CableRouter(
            self.termination_a,
            self.termination_a_type,
            termination_b,
            self.termination_b_type,
            media_type,
            enable_next_rack_hops=self.cleaned_data["allow_next_rack_hops"],
        )
        path = cleaned_data["cable_router"].get_path()
        if path is None:
            raise ValidationError(
                f"{self.termination_a.device} and {termination_b.device} are not connected"
            )

        cleaned_data["path"] = path

    def clean_termination_a_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_a_id"], "pk", None)

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data["termination_b_id"], "pk", None)


class CableRouterLinkToInterfaceForm(CableRouterLinkForm):
    termination_b_model = Interface

    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_b_device",
            "kind": "physical",
        },
    )

    class Meta(CableRouterLinkForm.Meta):
        pass


class CableRouterLinkToFrontPortForm(CableRouterLinkForm):
    termination_b_model = FrontPort

    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label="Name",
        disabled_indicator="cable",
        query_params={
            "device": "$termination_b_device",
        },
    )

    class Meta(CableRouterLinkForm.Meta):
        pass


class CableRouterVerifyForm(BootstrapMixin, Form):
    class Meta:
        fields = []
