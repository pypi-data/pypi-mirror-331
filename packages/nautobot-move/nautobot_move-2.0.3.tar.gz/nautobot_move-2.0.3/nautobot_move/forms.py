from django import forms
from django.db import transaction
from nautobot.apps.forms import DynamicModelChoiceField
from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import Status


class InstallBaseForm(forms.Form):
    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        self.component_types = [
            "console_ports",
            "console_server_ports",
            "power_ports",
            "power_outlets",
            "interfaces",
            "rear_ports",
            "front_ports",
            "device_bays",
        ]
        self.connectable_component_types = [
            "console_ports",
            "console_server_ports",
            "power_ports",
            "power_outlets",
            "interfaces",
            "rear_ports",
            "front_ports",
        ]

        super().__init__(*args, **kwargs)

    def get_inventory(self) -> Device:
        pass

    def get_planned(self) -> Device:
        pass

    def clean(self):
        super().clean()
        planned = self.get_planned()
        inventory = self.get_inventory()
        add_interfaces = self.cleaned_data.get("add_interfaces")
        delete_existing = self.cleaned_data.get("delete_existing")

        if inventory == planned:
            raise forms.ValidationError(
                "The inventory device is equal to the planned one"
            )

        if inventory.device_type != planned.device_type:
            move_devicetype = (
                str(inventory.device_type.manufacturer)
                + " "
                + str(inventory.device_type)
            )
            planned_devicetype = (
                str(planned.device_type.manufacturer) + " " + str(planned.device_type)
            )
            raise forms.ValidationError(
                f"The DeviceType of planned ({move_devicetype}) and inventory ({planned_devicetype}) device must be equal"
            )

        if not delete_existing:
            for component_type in self.connectable_component_types:
                prop = getattr(inventory, component_type)
                if prop.filter(cable__isnull=False).exists():
                    raise forms.ValidationError(
                        f"The inventory device still has connected {component_type}."
                    )

        if inventory.device_bays.filter(installed_device__isnull=False).exists():
            raise forms.ValidationError(
                "The inventory device still has connected device bays."
            )

        for component_type in self.component_types:
            inventory_prop = getattr(inventory, component_type)
            planned_prop = getattr(planned, component_type)
            # it is allowed to skip this check if add_interfaces is true, the missing devices should be synced in save()
            if not (add_interfaces and component_type == "interfaces"):

                if inventory_prop.count() != planned_prop.count():
                    raise forms.ValidationError(
                        f"The devices are incompatible: the number of {component_type} doesn’t match."
                    )

                for component in inventory_prop.all():
                    if not planned_prop.filter(name=component.name).exists():
                        raise forms.ValidationError(
                            f"The devices are incompatible: the {component_type} named {component.name} doesn’t exist on the device {planned.name}."
                        )

    def save(self):
        planned = self.get_planned()
        inventory = self.get_inventory()
        delete_existing = self.cleaned_data.get("delete_existing")
        add_interfaces = self.cleaned_data.get("add_interfaces")

        with transaction.atomic():

            if planned.interfaces.count() > 0:
                for interface in planned.interfaces.all():
                    # do the following only, if sync was requested
                    if add_interfaces:
                        # Check if interface is available by name in inventory
                        try:
                            inventory.interfaces.get(name=interface.name)
                        except Interface.DoesNotExist:
                            # ...if not move it from planned.instance
                            interface.device = inventory
                            interface.validated_save()
                            if interface.cable or interface.cable_id:
                                interface.cable.save()
                            # possibily remove interfaces from inventory if wanted, for now only additive sync is supported

                    inventory_interface = inventory.interfaces.get(name=interface.name)

                    # set "active" as default status if previously not set -> mandatory from nautobot v1.4.0+
                    inventory_interface.status = Status.objects.get_for_model(
                        Interface
                    ).get(name="Active")
                    # equalize status
                    if interface.status:
                        inventory_interface.status = interface.status
                    inventory_interface.validated_save()

                    # Transfer ip address information. The set() function adds ip addresses from planned device to the moved one
                    # and disassociates ip addresses which were previously on the interface
                    for ip_address in interface.ip_addresses.all():
                        ip_address.assigned_object = inventory_interface
                        # if one of the ip addresses is defined for use as primary address set it for the moved device
                        if ip_address == planned.primary_ip4:
                            # primary_ip4 has to be removed from planned device first for satisfying constraint
                            planned.primary_ip4 = None
                            planned.validated_save()
                        ip_address.validated_save()
                        inventory.primary_ip4 = ip_address
                        inventory_interface.tags.set(interface.tags.all())
                    # Add VLANs to moved device if exist
                    if interface.mode:
                        inventory_interface.mode = interface.mode
                        inventory_interface.untagged_vlan = interface.untagged_vlan
                        if interface.mode == "tagged":
                            inventory_interface.tagged_vlans.set(
                                interface.tagged_vlans.all()
                            )
                        inventory_interface.validated_save()

            for component_type in self.connectable_component_types:
                for component in getattr(planned, component_type).all():
                    this_component = getattr(inventory, component_type).get(
                        name=component.name
                    )
                    if this_component.cable and delete_existing:
                        this_component.cable.delete()
                    if not component.cable_id:
                        continue
                    component.cable.delete()
                    if component.cable.termination_a == component:
                        component.cable.termination_a = this_component
                    if component.cable.termination_b == component:
                        component.cable.termination_b = this_component

                    component.cable.pk = None
                    component.cable.save()

            inventory.device_bays.all().delete()
            planned.device_bays.all().update(device=inventory)

            inventory.name = planned.name
            inventory.platform = planned.platform
            inventory.status = planned.status
            inventory.role = planned.role
            inventory.location = planned.location
            inventory.rack = planned.rack
            inventory.position = planned.position
            inventory.face = planned.face
            inventory.tags.set(planned.tags.all())
            for custom_field in planned.cf:
                inventory.cf[custom_field] = planned.cf[custom_field]

            # add bgp routing instances
            if hasattr(planned, "bgp_routing_instances"):
                for bgp_routing_instance in planned.bgp_routing_instances.all():
                    bgp_routing_instance.device = inventory
                    bgp_routing_instance.validated_save()

            planned.delete()
            inventory.validated_save()

        return inventory


class InstallForm(InstallBaseForm):
    planned = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Planned",
        },
        help_text="The planned device where this device is going to be installed.",
    )
    delete_existing = forms.BooleanField(
        label="Remove connections",
        help_text="Should existing connections on the inventory device be deleted?",
        required=False,
    )

    add_interfaces = forms.BooleanField(
        label="Add missing interfaces",
        help_text="Interfaces on planned device will be added to inventory device",
        required=False,
    )

    def get_planned(self) -> Device:
        return Device.objects.get(pk=self.cleaned_data.get("planned").pk)

    def get_inventory(self) -> Device:
        return self.instance


class ReverseInstallForm(InstallBaseForm):
    inventory = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Inventory",
        },
        help_text="The inventory device that is going to be installed.",
    )
    delete_existing = forms.BooleanField(
        label="Remove connections",
        help_text="Should existing connections on the inventory device be deleted?",
        required=False,
    )

    add_interfaces = forms.BooleanField(
        label="Add missing interfaces",
        help_text="Interfaces on planned device will be added to inventory device",
        required=False,
    )

    def get_planned(self) -> Device:
        return self.instance

    def get_inventory(self) -> Device:
        return Device.objects.get(pk=self.cleaned_data.get("inventory").pk)
