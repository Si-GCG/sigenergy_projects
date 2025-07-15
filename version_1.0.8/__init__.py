"""The Sigenergy ESS integration."""

from __future__ import annotations
from . import pymodbus_compat

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry  #pylint: disable=no-name-in-module, syntax-error
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_SCAN_INTERVAL_HIGH,
    CONF_SCAN_INTERVAL_ALARM,
    CONF_SCAN_INTERVAL_MEDIUM,
    CONF_SCAN_INTERVAL_LOW,
    DEFAULT_SCAN_INTERVAL_HIGH,
    DEFAULT_SCAN_INTERVAL_ALARM,
    DEFAULT_SCAN_INTERVAL_MEDIUM,
    DEFAULT_SCAN_INTERVAL_LOW,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import SigenergyDataUpdateCoordinator
from .modbus import SigenergyModbusHub
from .const import CONF_PLANT_CONNECTION

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sigenergy ESS from a config entry."""
    _LOGGER.debug("async_setup_entry: Starting setup for entry: %s", entry.title)
    scan_interval = entry.data.get(CONF_PLANT_CONNECTION,
                                    {}).get(CONF_SCAN_INTERVAL_HIGH, 
                                            DEFAULT_SCAN_INTERVAL_HIGH)
    alarm_scan_interval = entry.data.get(CONF_PLANT_CONNECTION,
                                    {}).get(CONF_SCAN_INTERVAL_ALARM, 
                                            DEFAULT_SCAN_INTERVAL_ALARM)
    medium_scan_interval = entry.data.get(CONF_PLANT_CONNECTION,
                                    {}).get(CONF_SCAN_INTERVAL_MEDIUM, 
                                            DEFAULT_SCAN_INTERVAL_MEDIUM)
    low_scan_interval = entry.data.get(CONF_PLANT_CONNECTION,
                                    {}).get(CONF_SCAN_INTERVAL_LOW, 
                                            DEFAULT_SCAN_INTERVAL_LOW)
    host = entry.data[CONF_PLANT_CONNECTION][CONF_HOST]
    port = entry.data[CONF_PLANT_CONNECTION][CONF_PORT]

    _LOGGER.debug("async_setup_entry: Scan interval set to %s seconds", scan_interval)
    _LOGGER.debug("async_setup_entry: Alarm scan interval set to %s seconds", alarm_scan_interval)
    _LOGGER.debug("async_setup_entry: Medium scan interval set to %s seconds", medium_scan_interval)
    _LOGGER.debug("async_setup_entry: Low scan interval set to %s seconds", low_scan_interval)
    _LOGGER.debug("async_setup_entry: CONF_PLANT_CONNECTION: %s", entry.data[CONF_PLANT_CONNECTION])

    hub = SigenergyModbusHub(hass, entry)
    _LOGGER.debug("async_setup_entry: SigenergyModbusHub created: %s", hub)

    try:
        _LOGGER.debug("async_setup_entry: Connecting to Modbus hub...")
        await hub.async_connect(entry.data[CONF_PLANT_CONNECTION])
        _LOGGER.debug("async_setup_entry: Modbus hub connected successfully")
    except Exception as ex:
        _LOGGER.error(
            "async_setup_entry: Error connecting to Sigenergy system at %s:%s - %s",
            host,
            port,
            ex
        )
        raise ConfigEntryNotReady(f"Error connecting to Sigenergy system: {ex}") from ex

    coordinator = SigenergyDataUpdateCoordinator(
        hass,
        _LOGGER,
        hub=hub,
        name=f"{DOMAIN}_{host}_{port}",
        update_interval=timedelta(seconds=scan_interval),
        high_scan_interval=scan_interval,
        alarm_scan_interval=alarm_scan_interval,
        medium_scan_interval=medium_scan_interval,
        low_scan_interval=low_scan_interval,
    )
    _LOGGER.debug("async_setup_entry: SigenergyDataUpdateCoordinator created: %s", coordinator)

    _LOGGER.debug("async_setup_entry: Performing first refresh of coordinator...")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("async_setup_entry: Coordinator first refresh completed")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "hub": hub,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    _LOGGER.debug("async_setup_entry: Setup completed successfully for entry: %s", entry.title)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hub = hass.data[DOMAIN][entry.entry_id]["hub"]
        await hub.async_close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_migrate_entry(hass, entry: ConfigEntry):
    """Migrate old entry version."""
    _LOGGER.debug("Migrating configuration from version %s.%s", entry.version, entry.minor_version)

    if entry.version > 2 and entry.minor_version > 0:
        # This means the user has downgraded from a future version
        return False

    if entry.version == 1:

        scan_interval = entry.data.get(CONF_PLANT_CONNECTION,
                                        {}).get(CONF_SCAN_INTERVAL_HIGH, 
                                                DEFAULT_SCAN_INTERVAL_HIGH)

        # Add configuration changes for version 1.0
        new_data = {**entry.data}
        new_data[CONF_PLANT_CONNECTION][CONF_SCAN_INTERVAL_ALARM] = DEFAULT_SCAN_INTERVAL_ALARM \
            if DEFAULT_SCAN_INTERVAL_ALARM > scan_interval else scan_interval
        new_data[CONF_PLANT_CONNECTION][CONF_SCAN_INTERVAL_MEDIUM] = DEFAULT_SCAN_INTERVAL_MEDIUM \
            if DEFAULT_SCAN_INTERVAL_MEDIUM > scan_interval else scan_interval
        new_data[CONF_PLANT_CONNECTION][CONF_SCAN_INTERVAL_LOW] = DEFAULT_SCAN_INTERVAL_LOW \
            if DEFAULT_SCAN_INTERVAL_LOW > scan_interval else scan_interval


        hass.config_entries.async_update_entry(entry, data=new_data, minor_version=0, version=2)

    _LOGGER.debug("Migration to configuration version %s.%s successful", \
                  entry.version, entry.minor_version)

    return True
