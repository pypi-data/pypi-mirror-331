from dataclasses import dataclass
from typing import Any, Tuple

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from nautobot.apps.forms import DynamicModelChoiceField
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import (
    Cable,
    CablePath,
    Device,
    Interface,
    CableTermination,
    PathEndpoint,
)
from nautobot.extras.models import Status
from nautobot_cable_utils.models import CableInventoryItem

# TODO: Make all of this configurable
INTERFACE_POSTFIX = " (new)"

RELATIONSHIPS_TO_MOVE = ["InterfaceTenant"]
CUSTOM_FIELDS_TO_MOVE_DEVICE = [
    "contact",
    "drain",
    "location_comment",
    "rocev2",
    "cabdoc_id",
]
CUSTOM_FIELDS_TO_MOVE_INTERFACE = []

# Except interfaces, they are handled differently
CONNECTABLE_COMPONENT_TYPES = [
    "console_ports",
    "console_server_ports",
    "power_ports",
    "power_outlets",
    "rear_ports",
    "front_ports",
]


@dataclass
class InterfaceLut:
    interface_lut: dict[str, str]  # {"failed_interface1": "inventory_interface1", etc.}
    interfaces_create: list[str]


def migrate_interfaces(failed: Device, inventory: Device) -> InterfaceLut:
    interface_lut = {}
    interfaces_create = []

    # Needs to be cleared before moving IPs
    primary_ip4 = failed.primary_ip4
    primary_ip6 = failed.primary_ip6
    failed.primary_ip4 = None
    failed.primary_ip6 = None
    failed.validated_save()

    # create LAGs first
    lags_failed = list(failed.interfaces.filter(type=InterfaceTypeChoices.TYPE_LAG))
    non_lags_failed = list(
        failed.interfaces.exclude(type=InterfaceTypeChoices.TYPE_LAG)
    )
    interfaces_failed: list[Interface] = lags_failed + non_lags_failed

    for interface_failed in interfaces_failed:
        if interface_failed.is_connectable:
            inventory_create_name = f"{interface_failed.name}{INTERFACE_POSTFIX}"
        else:
            inventory_create_name = interface_failed.name
        interface_inventory, created = Interface.objects.get_or_create(
            device=inventory,
            name=interface_failed.name,
            defaults={
                "name": inventory_create_name,
                "status": interface_failed.status,
                "type": interface_failed.type,
            },
        )
        if created:
            interfaces_create.append(interface_inventory.name)
        else:
            interface_inventory.status = interface_failed.status

        interface_lut[interface_failed.name] = interface_inventory.name

        inventory_tags = interface_inventory.tags.exclude(
            _custom_field_data__device_specific=True
        )
        interface_inventory.tags.remove(*list(inventory_tags))
        failed_tags = interface_failed.tags.exclude(
            _custom_field_data__device_specific=True
        )
        interface_inventory.tags.add(*list(failed_tags))
        interface_failed.tags.remove(*list(failed_tags))

        interface_inventory.mode = interface_failed.mode
        interface_inventory.untagged_vlan = interface_failed.untagged_vlan
        interface_inventory.tagged_vlans.set(list(interface_failed.tagged_vlans.all()))

        interface_inventory.enabled = interface_failed.enabled
        interface_inventory.description = interface_failed.description
        interface_inventory.mtu = interface_failed.mtu
        interface_inventory.vrf = interface_failed.vrf

        for field in CUSTOM_FIELDS_TO_MOVE_INTERFACE:
            interface_inventory.cf[field] = interface_failed.cf.get(field)

        interface_inventory.ip_addresses.set(list(interface_failed.ip_addresses.all()))
        interface_failed.ip_addresses.set([])

        interface_inventory.validated_save()

        for association in interface_inventory.associations:
            if association.relationship.label in RELATIONSHIPS_TO_MOVE:
                association.delete()

        for association in interface_failed.associations:
            if association.relationship.label in RELATIONSHIPS_TO_MOVE:
                if association.get_destination() == interface_failed:
                    association.destination = interface_inventory
                    association.validated_save()
            elif association.get_source() == interface_failed:
                association.source = interface_inventory
                association.validated_save()

        if interface_failed.cable:
            reconnect_cable(interface_failed, interface_inventory)

    for interface_failed in interfaces_failed:
        if interface_failed.bridge:
            bridge = inventory.interfaces.get(
                name=interface_lut[interface_failed.bridge.name]
            )
            interface_inventory = inventory.interfaces.get(
                name=interface_lut[interface_failed.name]
            )
            interface_inventory.bridge = bridge
            interface_inventory.validated_save()
        if interface_failed.parent_interface:
            parent_interface = inventory.interfaces.get(
                name=interface_lut[interface_failed.parent_interface.name]
            )
            interface_inventory = inventory.interfaces.get(
                name=interface_lut[interface_failed.name]
            )
            interface_inventory.parent_interface = parent_interface
            interface_inventory.validated_save()
        if interface_failed.lag:
            lag = inventory.interfaces.get(
                name=interface_lut[interface_failed.lag.name]
            )
            interface_inventory = inventory.interfaces.get(
                name=interface_lut[interface_failed.name]
            )
            interface_inventory.lag = lag
            interface_inventory.validated_save()

    if primary_ip4:
        primary_ip4.refresh_from_db()
    if primary_ip6:
        primary_ip6.refresh_from_db()
    inventory.primary_ip4 = primary_ip4
    inventory.primary_ip6 = primary_ip6
    inventory.validated_save()

    return InterfaceLut(interface_lut, interfaces_create)


def migrate_components(failed: Device, inventory: Device):
    # TODO: device bays
    components_create = []
    for component_type in CONNECTABLE_COMPONENT_TYPES:
        for failed_component in getattr(failed, component_type).all():
            try:
                inventory_component = getattr(inventory, component_type).get(
                    name=failed_component.name
                )
            except ObjectDoesNotExist:
                inventory_component = failed_component
                # refetch the original component
                failed_component = getattr(failed, component_type).get(
                    name=inventory_component.name
                )
                # recreate inventory component
                inventory_component.pk = None
                inventory_component.name = (
                    f"{inventory_component.name}{INTERFACE_POSTFIX}"
                )
                components_create.append(inventory_component.name)
                inventory_component.device = inventory
                if isinstance(inventory_component, CableTermination):
                    inventory_component.cable = None
                    inventory_component._cable_peer = None
                if isinstance(inventory_component, PathEndpoint):
                    inventory_component._path = None
                inventory_component.validated_save()
            reconnect_cable(failed_component, inventory_component)
    return components_create


def reconnect_cable(old: CableTermination, new: CableTermination):
    if not old.cable:
        return
    # Taken from https://gitlab-ce.gwdg.de/gwdg-netz/nautobot-plugins/nautobot-cable-utils/-/blob/main/nautobot_cable_utils/views.py
    cable: Cable = old.cable

    if cable.termination_a == old:
        other_termination = cable.termination_b
        other_termination_side = "b"
    else:
        other_termination = cable.termination_a
        other_termination_side = "a"

    with transaction.atomic():
        try:
            if hasattr(cable.termination_a, "_path") and cable.termination_a._path_id:
                cable.termination_a._path = None
        except CablePath.DoesNotExist:
            pass
        try:
            if hasattr(cable.termination_b, "_path") and cable.termination_b._path_id:
                cable.termination_b._path = None
        except CablePath.DoesNotExist:
            pass

        cable_inventory_item = CableInventoryItem.objects.filter(cable=cable).first()
        cable.delete()
        cable.pk = None
        cable._state.adding = True

        cable.termination_a.cable = None
        cable.termination_b.cable = None

        if other_termination_side == "b":
            cable.termination_a = new
            cable.termination_b = other_termination
        else:
            cable.termination_a = other_termination
            cable.termination_b = new
        cable.validated_save()

        if cable_inventory_item:
            cable_inventory_item.cable = cable
            cable_inventory_item.validated_save()


def swap_devices(failed: Device, inventory: Device):
    if inventory.local_config_context_data_owner:
        raise forms.ValidationError(
            "Target Device already has local config context owned by someone else (maybe from git repository). Aborting to prevent inconsitencies."
        )
    if failed.local_config_context_data_owner:
        raise forms.ValidationError(
            "Source Device already has local config context owned by someone else (maybe from git repository). Aborting to prevent inconsitencies."
        )

    location = failed.location
    rack = failed.rack
    position = failed.position
    face = failed.face
    name = failed.name
    role = failed.role
    tenant = failed.tenant
    device_redundancy_group = failed.device_redundancy_group
    device_redundancy_group_priority = failed.device_redundancy_group_priority
    local_config_context_data = failed.local_config_context_data
    local_config_context_schema = failed.local_config_context_schema
    controller_managed_device_group = failed.controller_managed_device_group
    cluster = failed.cluster
    virtual_chassis = failed.virtual_chassis

    custom_fields = {}
    for field in CUSTOM_FIELDS_TO_MOVE_DEVICE:
        custom_fields[field] = failed.cf.get(field)

    failed.location = inventory.location
    failed.rack = inventory.rack
    failed.position = None
    failed.face = ""
    failed.name = f"{failed.serial} (failed)"
    failed.role = inventory.role
    failed.tenant = None
    failed.device_redundancy_group = None
    failed.device_redundancy_group_priority = None
    failed.local_config_context_data = None
    failed.local_config_context_schema = None
    failed.controller_managed_device_group = None
    failed.cluster = None
    failed.virtual_chassis = None

    inventory_position = inventory.position
    inventory_face = inventory.face

    inventory.location = location
    inventory.rack = rack
    # need to clear space in rack first when swapping two racked devices
    inventory.position = position
    inventory.face = face
    inventory.name = name
    inventory.role = role
    inventory.tenant = tenant
    inventory.device_redundancy_group = device_redundancy_group
    inventory.device_redundancy_group_priority = device_redundancy_group_priority
    for field in CUSTOM_FIELDS_TO_MOVE_DEVICE:
        inventory.cf[field] = custom_fields[field]
    if failed.comments:
        inventory.comments = (
            f"{inventory.comments}\nCopied from failed Device:\n{failed.comments}"
        )
    inventory.local_config_context_data = local_config_context_data
    inventory.local_config_context_schema = local_config_context_schema
    inventory.controller_managed_device_group = controller_managed_device_group
    inventory.cluster = cluster
    inventory.virtual_chassis = virtual_chassis

    inventory.status = Status.objects.get(name="Active")

    failed.validated_save()
    inventory.validated_save()

    failed.refresh_from_db()
    failed.position = inventory_position
    failed.face = inventory_face
    failed.validated_save()

    for association in inventory.associations:
        if association.relationship.label in RELATIONSHIPS_TO_MOVE:
            association.delete()

    for association in failed.associations:
        if association.relationship.label in RELATIONSHIPS_TO_MOVE:
            if association.get_destination() == failed:
                association.destination = inventory
                association.validated_save()
        elif association.get_source() == failed:
            association.source = inventory
            association.validated_save()

    for note in failed.notes.all():
        note.assigned_object = inventory
        note.validated_save()

    inventory.vrfs.set(list(failed.vrfs.all()))

    inventory_tags = inventory.tags.exclude(_custom_field_data__device_specific=True)
    inventory.tags.remove(*list(inventory_tags))
    failed_tags = failed.tags.exclude(_custom_field_data__device_specific=True)
    inventory.tags.add(*list(failed_tags))
    failed.tags.remove(*list(failed_tags))


def migrate_bgp(interface_lut: InterfaceLut, failed: Device, inventory: Device):
    for routing_instance in failed.bgp_routing_instances.all():
        routing_instance.device = inventory
        routing_instance.validated_save()

    for interface_failed in failed.interfaces.all():
        interface_inventory = inventory.interfaces.get(
            name=interface_lut.interface_lut[interface_failed.name]
        )
        for peer_endpoint in interface_failed.bgp_peer_endpoints.all():
            peer_endpoint.source_interface = interface_inventory
            peer_endpoint.validated_save()

        for peer_group in interface_failed.bgp_peer_groups.all():
            peer_group.source_interface = interface_inventory
            peer_group.validated_save()


def migrate_ethernet_segments(
    interface_lut: InterfaceLut, failed: Device, inventory: Device
):
    for interface_failed in failed.interfaces.all():
        interface_inventory = inventory.interfaces.get(
            name=interface_lut.interface_lut[interface_failed.name]
        )
        if hasattr(interface_failed, "ethernet_segment_membership"):
            ethernet_segment_membership = interface_failed.ethernet_segment_membership
            ethernet_segment_membership.interface = interface_inventory
            ethernet_segment_membership.validated_save()


def migrate_sfps(failed: Device, inventory: Device):
    for sfp in failed.sfps.all():
        sfp.assigned_device = inventory
        sfp.validated_save()


class ReplaceForm(forms.Form):
    failed = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Failed",
        },
        help_text="The failed device which this device is going to replace.",
    )

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        return super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        inventory = self.instance
        failed = self.cleaned_data.get("failed")
        if inventory == failed:
            raise forms.ValidationError("Can't replace device with itself")
        return super().clean()

    def save(self) -> Tuple[Device, InterfaceLut]:
        # Actually move device
        inventory = self.instance
        failed = self.cleaned_data.get("failed")

        with transaction.atomic():
            interface_lut = migrate_interfaces(failed, inventory)
            swap_devices(failed, inventory)
            migrate_bgp(interface_lut, failed, inventory)
            migrate_ethernet_segments(interface_lut, failed, inventory)
            migrate_sfps(failed, inventory)
            components_create = migrate_components(failed, inventory)

        return (inventory, failed, interface_lut, components_create)


class ReverseReplaceForm(forms.Form):
    inventory = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Inventory",
        },
        help_text="The inventory device with which this device is going to be replaced with.",
    )

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        return super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        failed = self.instance
        inventory = self.cleaned_data.get("inventory")
        if inventory == failed:
            raise forms.ValidationError("Can't replace device with itself")
        return super().clean()

    def save(self) -> Tuple[Device, InterfaceLut]:
        # Actually move device
        failed = self.instance
        inventory = self.cleaned_data.get("inventory")

        with transaction.atomic():
            interface_lut = migrate_interfaces(failed, inventory)
            swap_devices(failed, inventory)
            migrate_bgp(interface_lut, failed, inventory)
            migrate_ethernet_segments(interface_lut, failed, inventory)
            migrate_sfps(failed, inventory)
            components_create = migrate_components(failed, inventory)

        return (inventory, failed, interface_lut, components_create)
