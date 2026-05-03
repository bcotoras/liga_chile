"""Sensores para la integración Liga de Fútbol Chileno."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_PRIMERA_A_FIXTURES,
    KEY_PRIMERA_A_STANDINGS,
    KEY_PRIMERA_B_FIXTURES,
    KEY_PRIMERA_B_STANDINGS,
)
from .coordinator import LigaChileCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurar los sensores a partir de una config entry."""
    coordinator: LigaChileCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PrimeraATabla(coordinator, entry),
            PrimeraBTabla(coordinator, entry),
            PrimeraAFixtures(coordinator, entry),
            PrimeraBFixtures(coordinator, entry),
        ]
    )


# ---------------------------------------------------------------------------
# Clase base compartida
# ---------------------------------------------------------------------------

class _LigaChileBaseSensor(CoordinatorEntity[LigaChileCoordinator], SensorEntity):
    """Clase base para los sensores de Liga Chile."""

    def __init__(
        self,
        coordinator: LigaChileCoordinator,
        entry: ConfigEntry,
        name: str,
        unique_id: str,
    ) -> None:
        """Inicializar el sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._entry = entry

    @property
    def device_info(self) -> dict:
        """Información del dispositivo agrupador."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Liga de Fútbol Chileno",
            "manufacturer": "api-football.com",
            "model": "Cloud Polling",
        }


# ---------------------------------------------------------------------------
# Sensores de tabla de posiciones
# ---------------------------------------------------------------------------

class PrimeraATabla(_LigaChileBaseSensor):
    """Sensor con la tabla de posiciones de la Primera A."""

    def __init__(self, coordinator: LigaChileCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            name="Primera A - Tabla",
            unique_id="liga_chile_primera_a_tabla",
        )

    @property
    def native_value(self) -> str:
        """Nombre del líder actual o 'Sin datos'."""
        tabla = self._get_tabla()
        if not tabla:
            return "Sin datos"
        return tabla[0]["equipo"]

    @property
    def extra_state_attributes(self) -> dict:
        """Tabla completa de posiciones como atributo."""
        return {"tabla": self._get_tabla()}

    def _get_tabla(self) -> list[dict]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(KEY_PRIMERA_A_STANDINGS, [])


class PrimeraBTabla(_LigaChileBaseSensor):
    """Sensor con la tabla de posiciones de la Primera B."""

    def __init__(self, coordinator: LigaChileCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            name="Primera B - Tabla",
            unique_id="liga_chile_primera_b_tabla",
        )

    @property
    def native_value(self) -> str:
        """Nombre del líder actual o 'Sin datos'."""
        tabla = self._get_tabla()
        if not tabla:
            return "Sin datos"
        return tabla[0]["equipo"]

    @property
    def extra_state_attributes(self) -> dict:
        """Tabla completa de posiciones como atributo."""
        return {"tabla": self._get_tabla()}

    def _get_tabla(self) -> list[dict]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(KEY_PRIMERA_B_STANDINGS, [])


# ---------------------------------------------------------------------------
# Sensores de fixtures (partidos)
# ---------------------------------------------------------------------------

class PrimeraAFixtures(_LigaChileBaseSensor):
    """Sensor con los partidos próximos de la Primera A."""

    def __init__(self, coordinator: LigaChileCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            name="Primera A - Partidos",
            unique_id="liga_chile_primera_a_partidos",
        )

    @property
    def native_value(self) -> int:
        """Número de partidos en el rango consultado."""
        return len(self._get_fixtures())

    @property
    def extra_state_attributes(self) -> dict:
        """Partidos y timestamp de última actualización."""
        return {
            "partidos": self._get_fixtures(),
            "ultima_actualizacion": _now_iso(),
        }

    def _get_fixtures(self) -> list[dict]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(KEY_PRIMERA_A_FIXTURES, [])


class PrimeraBFixtures(_LigaChileBaseSensor):
    """Sensor con los partidos próximos de la Primera B."""

    def __init__(self, coordinator: LigaChileCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            name="Primera B - Partidos",
            unique_id="liga_chile_primera_b_partidos",
        )

    @property
    def native_value(self) -> int:
        """Número de partidos en el rango consultado."""
        return len(self._get_fixtures())

    @property
    def extra_state_attributes(self) -> dict:
        """Partidos y timestamp de última actualización."""
        return {
            "partidos": self._get_fixtures(),
            "ultima_actualizacion": _now_iso(),
        }

    def _get_fixtures(self) -> list[dict]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(KEY_PRIMERA_B_FIXTURES, [])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Retorna el timestamp actual en formato ISO 8601."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
