"""Integración Liga de Fútbol Chileno para Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import LigaChileCoordinator

_LOGGER = logging.getLogger(__name__)

# Plataformas que expone esta integración
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurar la integración a partir de una config entry."""
    coordinator = LigaChileCoordinator(hass, entry)

    # Realizar la primera actualización de datos. Si falla, lanzar ConfigEntryNotReady
    # para que Home Assistant reintente más tarde.
    await coordinator.async_config_entry_first_refresh()

    # Guardar el coordinator en hass.data para que las plataformas lo accedan
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Registrar las plataformas (usa el método moderno, no el deprecado)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Recargar la entry cuando el usuario cambie las opciones
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recargar la integración cuando cambian las opciones."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descargar la integración cuando se elimina la config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
