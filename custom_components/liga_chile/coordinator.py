"""Coordinator para la integración Liga de Fútbol Chileno."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_BASE_URL,
    CHILE_TZ,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_SEASON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FIXTURES_DAYS_AHEAD,
    KEY_PRIMERA_A_FIXTURES,
    KEY_PRIMERA_A_STANDINGS,
    KEY_PRIMERA_B_FIXTURES,
    KEY_PRIMERA_B_STANDINGS,
    PRIMERA_A_ID,
    PRIMERA_B_ID,
)

_LOGGER = logging.getLogger(__name__)


class LigaChileCoordinator(DataUpdateCoordinator):
    """Coordinator que obtiene datos de standings y fixtures de la API."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Inicializar el coordinator."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self._api_key: str = entry.data[CONF_API_KEY]
        self._season: str = entry.data[CONF_SEASON]

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _build_headers(self) -> dict[str, str]:
        """Construir headers de autenticación para la API."""
        return {"x-apisports-key": self._api_key}

    async def _fetch_json(
        self, session: aiohttp.ClientSession, url: str, params: dict | None = None
    ) -> dict:
        """Realizar una llamada GET y retornar el JSON. Lanza UpdateFailed si hay error."""
        try:
            async with asyncio.timeout(30):
                async with session.get(
                    url, headers=self._build_headers(), params=params
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(
                            f"La API retornó código HTTP {response.status} para {url}"
                        )
                    return await response.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout al conectar con la API: {url}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error de red al conectar con la API: {err}") from err

    def _parse_standings(self, raw: dict) -> list[dict]:
        """
        Parsear la respuesta de standings de la API y retornar lista de posiciones.

        Retorna lista de dicts con claves:
            pos, equipo, logo, pts, pj, pg, pe, pp, gf, gc, dg
        """
        try:
            groups = raw["response"][0]["league"]["standings"]
            # standings puede tener varios grupos (ej. apertura/clausura).
            # Usamos el primer grupo que es la tabla general.
            entries = groups[0]
        except (KeyError, IndexError, TypeError):
            _LOGGER.warning("Respuesta de standings inesperada: %s", raw)
            return []

        result: list[dict] = []
        for entry in entries:
            try:
                all_stats = entry["all"]
                result.append(
                    {
                        "pos": entry["rank"],
                        "equipo": entry["team"]["name"],
                        "logo": entry["team"].get("logo", ""),
                        "pts": entry["points"],
                        "pj": all_stats["played"],
                        "pg": all_stats["win"],
                        "pe": all_stats["draw"],
                        "pp": all_stats["lose"],
                        "gf": all_stats["goals"]["for"],
                        "gc": all_stats["goals"]["against"],
                        "dg": entry["goalsDiff"],
                    }
                )
            except (KeyError, TypeError) as err:
                _LOGGER.warning("Error parseando entrada de standings: %s | %s", entry, err)

        return result

    def _parse_fixtures(self, raw: dict) -> list[dict]:
        """
        Parsear la respuesta de fixtures de la API.

        Retorna lista de dicts con claves:
            fecha, hora, jornada, local, logo_local, visita, logo_visita,
            goles_local, goles_visita, estado
        """
        try:
            items = raw["response"]
        except (KeyError, TypeError):
            _LOGGER.warning("Respuesta de fixtures inesperada: %s", raw)
            return []

        # Importar aquí para evitar imports circulares en tiempo de módulo
        from zoneinfo import ZoneInfo  # disponible en Python 3.9+

        chile_tz = ZoneInfo(CHILE_TZ)

        result: list[dict] = []
        for item in items:
            try:
                fixture = item["fixture"]
                teams = item["teams"]
                goals = item["goals"]
                league = item["league"]

                # Convertir fecha UTC a hora de Chile
                date_str: str = fixture["date"]
                dt_utc = datetime.fromisoformat(date_str)
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                dt_chile = dt_utc.astimezone(chile_tz)

                estado_short: str = fixture["status"]["short"]
                estado_long: str = fixture["status"]["long"]

                # Mapear estados a texto legible en español
                estado_map = {
                    "NS": "Por jugar",
                    "1H": "Primer tiempo",
                    "HT": "Entretiempo",
                    "2H": "Segundo tiempo",
                    "ET": "Tiempo extra",
                    "P": "Penales",
                    "FT": "Finalizado",
                    "AET": "Finalizado (ET)",
                    "PEN": "Finalizado (Pen.)",
                    "BT": "Descanso",
                    "SUSP": "Suspendido",
                    "INT": "Interrumpido",
                    "PST": "Postergado",
                    "CANC": "Cancelado",
                    "ABD": "Abandonado",
                    "AWD": "Ganado por W.O.",
                    "WO": "W.O.",
                    "LIVE": "En juego",
                }
                estado = estado_map.get(estado_short, estado_long)

                # Parsear jornada: "Regular Season - 15" → "Jornada 15"
                round_raw: str = league.get("round", "")
                jornada = _parse_round(round_raw)

                result.append(
                    {
                        "fecha": dt_chile.strftime("%Y-%m-%d"),
                        "hora": dt_chile.strftime("%H:%M"),
                        "jornada": jornada,
                        "local": teams["home"]["name"],
                        "logo_local": teams["home"].get("logo", ""),
                        "visita": teams["away"]["name"],
                        "logo_visita": teams["away"].get("logo", ""),
                        "goles_local": goals.get("home"),
                        "goles_visita": goals.get("away"),
                        "estado": estado,
                    }
                )
            except (KeyError, TypeError, ValueError) as err:
                _LOGGER.warning("Error parseando fixture: %s | %s", item, err)

        # Ordenar por fecha/hora ascendente
        result.sort(key=lambda x: (x["fecha"], x["hora"]))
        return result

    # ------------------------------------------------------------------
    # Método principal del coordinator
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        """
        Obtener todos los datos necesarios de la API.

        Realiza 4 llamadas en paralelo:
        1. Standings Primera A
        2. Standings Primera B
        3. Fixtures Primera A (hoy + 14 días)
        4. Fixtures Primera B (hoy + 14 días)
        """
        today = datetime.now(tz=timezone.utc).date()
        end_date = today + timedelta(days=FIXTURES_DAYS_AHEAD)
        date_from = today.isoformat()
        date_to = end_date.isoformat()

        standings_a_url = f"{API_BASE_URL}/standings"
        standings_b_url = f"{API_BASE_URL}/standings"
        fixtures_a_url = f"{API_BASE_URL}/fixtures"
        fixtures_b_url = f"{API_BASE_URL}/fixtures"

        params_standings_a = {"league": PRIMERA_A_ID, "season": self._season}
        params_standings_b = {"league": PRIMERA_B_ID, "season": self._season}
        params_fixtures_a = {
            "league": PRIMERA_A_ID,
            "season": self._season,
            "from": date_from,
            "to": date_to,
        }
        params_fixtures_b = {
            "league": PRIMERA_B_ID,
            "season": self._season,
            "from": date_from,
            "to": date_to,
        }

        async with aiohttp.ClientSession() as session:
            (
                raw_standings_a,
                raw_standings_b,
                raw_fixtures_a,
                raw_fixtures_b,
            ) = await asyncio.gather(
                self._fetch_json(session, standings_a_url, params_standings_a),
                self._fetch_json(session, standings_b_url, params_standings_b),
                self._fetch_json(session, fixtures_a_url, params_fixtures_a),
                self._fetch_json(session, fixtures_b_url, params_fixtures_b),
            )

        return {
            KEY_PRIMERA_A_STANDINGS: self._parse_standings(raw_standings_a),
            KEY_PRIMERA_B_STANDINGS: self._parse_standings(raw_standings_b),
            KEY_PRIMERA_A_FIXTURES: self._parse_fixtures(raw_fixtures_a),
            KEY_PRIMERA_B_FIXTURES: self._parse_fixtures(raw_fixtures_b),
        }


# ------------------------------------------------------------------
# Helpers a nivel de módulo
# ------------------------------------------------------------------

def _parse_round(round_raw: str) -> str:
    """
    Convertir el string de jornada de la API a texto legible.

    Ejemplos:
      "Regular Season - 15"  → "Jornada 15"
      "Apertura - 8"         → "Apertura 8"
      "Clausura - 3"         → "Clausura 3"
    """
    if not round_raw:
        return ""

    separators = [" - ", " – ", "-"]
    for sep in separators:
        if sep in round_raw:
            parts = round_raw.split(sep, 1)
            prefix = parts[0].strip()
            number = parts[1].strip() if len(parts) > 1 else ""

            if prefix.lower() in ("regular season", "temporada regular"):
                return f"Jornada {number}" if number else "Jornada"
            # Para otros casos (Apertura, Clausura, etc.) conservar el prefijo
            return f"{prefix} {number}".strip()

    return round_raw
