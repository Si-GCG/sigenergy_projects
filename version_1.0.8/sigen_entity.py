"""Base entity for Sigenergy ESS integration."""
from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity  # pylint: disable=syntax-error

from .const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_INVERTER,
    DEVICE_TYPE_AC_CHARGER,
    DEVICE_TYPE_DC_CHARGER,
)
from .coordinator import SigenergyDataUpdateCoordinator
from .common import generate_unique_entity_id, generate_device_id

_LOGGER = logging.getLogger(__name__)


class SigenergyEntity(CoordinatorEntity):
    """Base representation of a Sigenergy entity."""

    _attr_has_entity_name = True # Use default HA entity naming

    def __init__(
        self,
        coordinator: SigenergyDataUpdateCoordinator,
        description: Any, # Use Any for broader compatibility initially
        name: str,
        device_type: str,
        device_id: Optional[str] = None, # Changed from int to str for consistency
        device_name: Optional[str] = "",
        device_info: Optional[DeviceInfo] = None,
        pv_string_idx: Optional[int] = None,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self.hub = coordinator.hub
        # Note: _attr_name is handled by _attr_has_entity_name = True and description.name
        # self._attr_name = name # We might not need this if using has_entity_name=True
        self._device_type = device_type
        self._device_id = device_id # Store original ID (e.g., slave ID for AC charger)
        self._device_name = device_name # Store device name (e.g., "Inverter 1", "Plant", "AC Charger 1")
        self._pv_string_idx = pv_string_idx
        self._device_info_override = device_info

        # Set unique ID
        self._attr_unique_id = generate_unique_entity_id(
            device_type, device_name, coordinator, description.key, pv_string_idx
        )

        # Set device info (use provided device_info if available)
        if self._device_info_override:
            self._attr_device_info = self._device_info_override
            return

        # Generate device info based on type
        config_entry_id = coordinator.hub.config_entry.entry_id
        plant_device_identifier = (DOMAIN, f"{config_entry_id}_plant")

        if device_type == DEVICE_TYPE_PLANT:
            self._attr_device_info = DeviceInfo(
                identifiers={plant_device_identifier},
                name=device_name, # Should be the plant name
                manufacturer="Sigenergy",
                model="Energy Storage System",
            )
        elif device_type == DEVICE_TYPE_INVERTER:
            model = None
            serial_number = None
            sw_version = None
            if coordinator.data and "inverters" in coordinator.data:
                inverter_data = coordinator.data["inverters"].get(device_name, {})
                model = inverter_data.get("inverter_model_type")
                serial_number = inverter_data.get("inverter_serial_number")
                sw_version = inverter_data.get("inverter_machine_firmware_version")

            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{config_entry_id}_{generate_device_id(device_name)}")},
                name=device_name,
                manufacturer="Sigenergy",
                model=model,
                serial_number=serial_number,
                sw_version=sw_version,
                via_device=plant_device_identifier,
            )
        elif device_type == DEVICE_TYPE_AC_CHARGER:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{config_entry_id}_{generate_device_id(device_name)}")},
                name=device_name,
                manufacturer="Sigenergy",
                model="AC Charger",
                via_device=plant_device_identifier,
            )
        elif device_type == DEVICE_TYPE_DC_CHARGER:
            # DC Charger is often part of the inverter, use provided device_info
            # If no specific device_info provided, link to the parent inverter
            # This case might need refinement based on how DC chargers are represented
            # For now, assume device_info is provided during setup for DC chargers
            # If not, create a basic one linked to the plant.
             _LOGGER.warning("DC Charger device_info not provided for %s, linking to plant.", name)
             self._attr_device_info = DeviceInfo(
                 identifiers={(DOMAIN, f"{config_entry_id}_{generate_device_id(device_name)}")}, # Needs a unique ID scheme
                 name=device_name, # e.g., "Inverter 1 DC Charger"
                 manufacturer="Sigenergy",
                 model="DC Charger", # Or fetch specific model if available
                 via_device=plant_device_identifier, # Or link to parent inverter if possible
             )
        else:
            _LOGGER.error("Unknown device type for entity %s: %s", self._attr_unique_id, device_type)
            # Fallback device info linked to plant
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{config_entry_id}_{generate_device_id(device_name)}")},
                name=device_name,
                manufacturer="Sigenergy",
                via_device=plant_device_identifier,
            )

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Checks coordinator status and optionally device-specific data availability.
        """
        if not self.coordinator.last_update_success:
            return False

        if self.coordinator.data is None:
            return False

        # Default availability check (can be overridden by subclasses)
        if self._device_type == DEVICE_TYPE_PLANT:
            return "plant" in self.coordinator.data
        elif self._device_type == DEVICE_TYPE_INVERTER:
            return (
                "inverters" in self.coordinator.data
                and self._device_name in self.coordinator.data["inverters"]
            )
        elif self._device_type == DEVICE_TYPE_AC_CHARGER:
            # AC Chargers are identified by device_name in the connections dict,
            # but their data might be keyed by slave_id (_device_id) in coordinator.data
            # Let's assume data is keyed by device_name for consistency for now.
            # If issues arise, we might need to check coordinator.data["ac_chargers"].get(self._device_id)
            return (
                "ac_chargers" in self.coordinator.data
                and self._device_name in self.coordinator.data["ac_chargers"]
            )
        elif self._device_type == DEVICE_TYPE_DC_CHARGER:
             # DC Charger data might be within the parent inverter's data
             # Check if parent inverter exists first
             parent_inverter_name = self._device_name.replace(" DC Charger", "").strip() if self._device_name else None
             if parent_inverter_name and "inverters" in self.coordinator.data and parent_inverter_name in self.coordinator.data["inverters"]:
                 # Further checks for specific DC charger keys can be added if needed
                 return True
             return False # Cannot determine availability if parent inverter is missing

        # Fallback for unknown types or if specific checks aren't needed
        return True