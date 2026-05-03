"""Flujo de configuración para Liga de Fútbol Chileno."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import API_BASE_URL, CONF_API_KEY, CONF_SCAN_INTERVAL, CONF_SEASON, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Esquema del formulario de configuración
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Optional(CONF_SEASON, default="2025"): str,
    }
)


async def _validate_api_key(api_key: str) -> None:
    """
    Validar la API key realizando una llamada al endpoint /status.

    Lanza:
        CannotConnect  — si no se puede establecer conexión
        InvalidAuth    — si la API key es inválida o rechazada
    """
    url = f"{API_BASE_URL}/status"
    headers = {"x-apisports-key": api_key}

    try:
        async with asyncio.timeout(15):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 401:
                        raise InvalidAuth
                    if response.status != 200:
                        raise CannotConnect

                    data = await response.json()

                    # La API retorna {"errors": {"token": "..."}} si el token es inválido
                    errors = data.get("errors", {})
                    if errors and "token" in errors:
                        raise InvalidAuth

                    # Verificar que la respuesta tiene datos válidos de cuenta
                    if not data.get("response"):
                        raise InvalidAuth

    except asyncio.TimeoutError as err:
        raise CannotConnect from err
    except aiohttp.ClientError as err:
        raise CannotConnect from err


class LigaChileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flujo de configuración para Liga de Fútbol Chileno."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Retornar el flujo de opciones."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Manejar el paso inicial del flujo de configuración."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key: str = user_input[CONF_API_KEY].strip()
            season: str = user_input.get(CONF_SEASON, "2025").strip()

            try:
                await _validate_api_key(api_key)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Error inesperado durante la validación de la API key")
                errors["base"] = "unknown"
            else:
                # Evitar entradas duplicadas para la misma API key
                await self.async_set_unique_id(api_key[:8])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Liga de Fútbol Chileno",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_SEASON: season,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


# ---------------------------------------------------------------------------
# Options Flow
# ---------------------------------------------------------------------------

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Flujo de opciones: permite cambiar el intervalo de actualización."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Mostrar y procesar el formulario de opciones."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                        vol.Coerce(int), vol.Range(min=30, max=1440)
                    )
                }
            ),
        )


# ---------------------------------------------------------------------------
# Excepciones internas del flujo
# ---------------------------------------------------------------------------

class CannotConnect(Exception):
    """No se pudo conectar con la API."""


class InvalidAuth(Exception):
    """La API key es inválida."""
