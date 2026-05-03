"""Constantes para la integración Liga de Fútbol Chileno."""

DOMAIN = "liga_chile"

# Claves de configuración
CONF_API_KEY = "api_key"
CONF_SEASON = "season"
CONF_SCAN_INTERVAL = "scan_interval"

# IDs de ligas en api-football.com
PRIMERA_A_ID = 265
PRIMERA_B_ID = 266

# URL base de la API
API_BASE_URL = "https://v3.football.api-sports.io"

# Intervalo de actualización en minutos
# El free tier de api-football.com tiene un límite de 100 req/día.
# 4 llamadas por ciclo → máximo 25 ciclos/día → ~57 min mínimo entre ciclos.
# Con 60 min se usan ~96 req/día, justo bajo el límite del tier gratuito.
DEFAULT_SCAN_INTERVAL = 60

# Zona horaria de Chile
CHILE_TZ = "America/Santiago"

# Número de días hacia adelante para consultar fixtures
FIXTURES_DAYS_AHEAD = 14

# Claves del dict retornado por el coordinator
KEY_PRIMERA_A_STANDINGS = "primera_a_standings"
KEY_PRIMERA_B_STANDINGS = "primera_b_standings"
KEY_PRIMERA_A_FIXTURES = "primera_a_fixtures"
KEY_PRIMERA_B_FIXTURES = "primera_b_fixtures"
