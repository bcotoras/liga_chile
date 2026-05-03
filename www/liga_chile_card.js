/**
 * Liga Chile Card — Tarjeta Lovelace para Home Assistant
 *
 * Muestra tabla de posiciones o fixture list de la Primera A / Primera B
 * del fútbol chileno usando los sensores de la integración liga_chile.
 *
 * Uso en Lovelace YAML:
 *   type: custom:liga-chile-card
 *   entity: sensor.primera_a_tabla
 *   card_type: tabla       # "tabla" o "fixtures"
 *   title: Primera A       # opcional
 */

// ---------------------------------------------------------------------------
// Estilos CSS compartidos
// ---------------------------------------------------------------------------
const SHARED_STYLES = `
  :host {
    display: block;
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
  }

  ha-card {
    padding: 0;
    overflow: hidden;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 16px 8px;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--primary-text-color);
    border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.12));
  }

  .card-header .title-icon {
    font-size: 1.4rem;
  }

  .card-content {
    padding: 0 0 8px;
    overflow-x: auto;
  }

  .no-data {
    padding: 24px 16px;
    text-align: center;
    color: var(--secondary-text-color);
    font-style: italic;
  }

  /* ---- Tabla de posiciones ---- */
  table.standings-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }

  table.standings-table thead tr {
    background: var(--table-row-alternative-background-color,
                    var(--secondary-background-color, #f5f5f5));
    color: var(--secondary-text-color);
  }

  table.standings-table th {
    padding: 6px 8px;
    text-align: center;
    font-weight: 500;
    white-space: nowrap;
    border-bottom: 2px solid var(--divider-color, rgba(0,0,0,0.12));
  }

  table.standings-table th.col-equipo {
    text-align: left;
    padding-left: 12px;
  }

  table.standings-table td {
    padding: 5px 8px;
    text-align: center;
    border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.06));
    color: var(--primary-text-color);
  }

  table.standings-table td.col-equipo {
    text-align: left;
    padding-left: 8px;
    white-space: nowrap;
  }

  table.standings-table .team-cell {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  table.standings-table .team-cell img {
    width: 20px;
    height: 20px;
    object-fit: contain;
  }

  table.standings-table .pos-cell {
    font-weight: 500;
    min-width: 24px;
  }

  /* Clasificaciones */
  tr.zone-libertadores {
    background: rgba(76, 175, 80, 0.12);   /* verde */
  }
  tr.zone-libertadores td.pos-cell {
    border-left: 3px solid #4CAF50;
  }

  tr.zone-sudamericana {
    background: rgba(33, 150, 243, 0.10);  /* azul claro */
  }
  tr.zone-sudamericana td.pos-cell {
    border-left: 3px solid #2196F3;
  }

  tr.zone-descenso {
    background: rgba(244, 67, 54, 0.10);   /* rojo */
  }
  tr.zone-descenso td.pos-cell {
    border-left: 3px solid #F44336;
  }

  /* Leyenda */
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 8px 12px;
    font-size: 0.75rem;
    color: var(--secondary-text-color);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .legend-dot.libertadores { background: #4CAF50; }
  .legend-dot.sudamericana { background: #2196F3; }
  .legend-dot.descenso     { background: #F44336; }

  /* ---- Fixture list ---- */
  .fixture-date-group {
    margin: 0;
  }

  .fixture-date-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px 4px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--secondary-text-color);
    background: var(--secondary-background-color, #f5f5f5);
    border-top: 1px solid var(--divider-color, rgba(0,0,0,0.08));
    border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.08));
  }

  .fixture-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.06));
  }

  .fixture-row:last-child {
    border-bottom: none;
  }

  .team-home, .team-away {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .team-home {
    justify-content: flex-end;
    text-align: right;
  }

  .team-away {
    justify-content: flex-start;
    text-align: left;
  }

  .team-home img, .team-away img {
    width: 24px;
    height: 24px;
    object-fit: contain;
    flex-shrink: 0;
  }

  .fixture-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    min-width: 70px;
  }

  .fixture-score {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--primary-text-color);
    letter-spacing: 2px;
  }

  .fixture-score.pending {
    font-size: 0.9rem;
    font-weight: 400;
    color: var(--secondary-text-color);
    letter-spacing: 1px;
  }

  .fixture-status {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }

  .fixture-jornada {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }

  .fixture-status.live {
    color: #F44336;
    font-weight: 600;
  }
`;

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

/** Estados que representan un partido en juego */
const LIVE_STATES = new Set([
  "Primer tiempo",
  "Entretiempo",
  "Segundo tiempo",
  "Tiempo extra",
  "Penales",
  "En juego",
]);

/** Estados que representan un partido ya terminado */
const FINISHED_STATES = new Set([
  "Finalizado",
  "Finalizado (ET)",
  "Finalizado (Pen.)",
  "W.O.",
  "Ganado por W.O.",
]);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Formatear una fecha "YYYY-MM-DD" a texto legible en español.
 * @param {string} dateStr
 * @returns {string}
 */
function formatDateLabel(dateStr) {
  const [year, month, day] = dateStr.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString("es-CL", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

/**
 * Crear elemento img con fallback si la URL falla.
 * @param {string} src
 * @param {string} alt
 * @returns {HTMLImageElement}
 */
function teamLogo(src, alt) {
  const img = document.createElement("img");
  img.src = src || "";
  img.alt = alt || "";
  img.onerror = () => { img.style.display = "none"; };
  return img;
}

/**
 * Escapar texto para inserción segura en HTML.
 * @param {string|number} value
 * @returns {string}
 */
function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------

class LigaChileCard extends HTMLElement {
  // -------------------------------------------------------------------------
  // Ciclo de vida del custom element
  // -------------------------------------------------------------------------

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  /** Llamado por HA cuando se asigna el objeto hass. */
  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  /** Llamado por HA con la configuración YAML de la tarjeta. */
  setConfig(config) {
    if (!config.entity) {
      throw new Error("La configuración requiere el campo 'entity'.");
    }
    if (!config.card_type || !["tabla", "fixtures"].includes(config.card_type)) {
      throw new Error("El campo 'card_type' debe ser 'tabla' o 'fixtures'.");
    }
    this._config = config;
    this._render();
  }

  // -------------------------------------------------------------------------
  // Renderizado principal
  // -------------------------------------------------------------------------

  _render() {
    if (!this._config || !this._hass) return;

    const entityId = this._config.entity;
    const stateObj = this._hass.states[entityId];

    const shadow = this.shadowRoot;
    shadow.innerHTML = "";

    // Inyectar estilos
    const style = document.createElement("style");
    style.textContent = SHARED_STYLES;
    shadow.appendChild(style);

    // Crear card
    const card = document.createElement("ha-card");

    // Header
    const cardType = this._config.card_type;
    const defaultTitle =
      cardType === "tabla"
        ? (entityId.includes("primera_b") ? "Primera B — Tabla" : "Primera A — Tabla")
        : (entityId.includes("primera_b") ? "Primera B — Partidos" : "Primera A — Partidos");

    const title = this._config.title || defaultTitle;
    const icon = cardType === "tabla" ? "🏆" : "⚽";

    const header = document.createElement("div");
    header.className = "card-header";
    header.innerHTML = `<span class="title-icon">${icon}</span><span>${esc(title)}</span>`;
    card.appendChild(header);

    // Contenido
    const content = document.createElement("div");
    content.className = "card-content";

    if (!stateObj) {
      content.innerHTML = `<div class="no-data">Entidad no encontrada: ${esc(entityId)}</div>`;
    } else {
      const attrs = stateObj.attributes || {};
      if (cardType === "tabla") {
        content.appendChild(this._renderTabla(attrs));
      } else {
        content.appendChild(this._renderFixtures(attrs));
      }
    }

    card.appendChild(content);
    shadow.appendChild(card);
  }

  // -------------------------------------------------------------------------
  // Renderizado de tabla de posiciones
  // -------------------------------------------------------------------------

  /**
   * @param {Object} attrs - atributos del sensor
   * @returns {DocumentFragment}
   */
  _renderTabla(attrs) {
    const fragment = document.createDocumentFragment();
    const tabla = attrs.tabla;

    if (!Array.isArray(tabla) || tabla.length === 0) {
      const div = document.createElement("div");
      div.className = "no-data";
      div.textContent = "Sin datos de tabla disponibles.";
      fragment.appendChild(div);
      return fragment;
    }

    const totalEquipos = tabla.length;

    // Determinar zonas según total de equipos
    // Primera A: 16 equipos — primeros 2 Libertadores, 3-4 Sudamericana, últimos 2 descenso
    // Primera B: variable — últimos 2 descenso, primeros 2 ascenso (Libertadores slot)
    const liberZone = 2;
    const sudaZone = 4;
    const descensoStart = totalEquipos - 1; // últimas 2 posiciones (index base 0)

    const table = document.createElement("table");
    table.className = "standings-table";

    // Encabezado
    table.innerHTML = `
      <thead>
        <tr>
          <th class="col-equipo" style="width:24px"></th>
          <th class="col-equipo">Equipo</th>
          <th title="Puntos">Pts</th>
          <th title="Partidos jugados">PJ</th>
          <th title="Partidos ganados">PG</th>
          <th title="Partidos empatados">PE</th>
          <th title="Partidos perdidos">PP</th>
          <th title="Goles a favor">GF</th>
          <th title="Goles en contra">GC</th>
          <th title="Diferencia de goles">DG</th>
        </tr>
      </thead>
    `;

    const tbody = document.createElement("tbody");

    for (const row of tabla) {
      const pos = row.pos;
      const tr = document.createElement("tr");

      // Clase de zona
      if (pos <= liberZone) {
        tr.className = "zone-libertadores";
      } else if (pos <= sudaZone) {
        tr.className = "zone-sudamericana";
      } else if (pos >= totalEquipos - 1) {
        tr.className = "zone-descenso";
      }

      // Celda de posición
      const tdPos = document.createElement("td");
      tdPos.className = "pos-cell";
      tdPos.textContent = pos;

      // Celda de equipo con logo
      const tdEquipo = document.createElement("td");
      tdEquipo.className = "col-equipo";
      const teamCell = document.createElement("div");
      teamCell.className = "team-cell";
      if (row.logo) {
        teamCell.appendChild(teamLogo(row.logo, row.equipo));
      }
      const nameSpan = document.createElement("span");
      nameSpan.textContent = row.equipo || "";
      teamCell.appendChild(nameSpan);
      tdEquipo.appendChild(teamCell);

      // Celdas numéricas
      const numFields = [
        row.pts, row.pj, row.pg, row.pe, row.pp, row.gf, row.gc,
        row.dg >= 0 ? `+${row.dg}` : row.dg,
      ];
      const cells = [tdPos, tdEquipo, ...numFields.map((v) => {
        const td = document.createElement("td");
        td.textContent = v ?? "";
        return td;
      })];

      cells.forEach((td) => tr.appendChild(td));
      tbody.appendChild(tr);
    }

    table.appendChild(tbody);
    fragment.appendChild(table);

    // Leyenda de colores
    const legend = document.createElement("div");
    legend.className = "legend";
    legend.innerHTML = `
      <span class="legend-item">
        <span class="legend-dot libertadores"></span>Copa Libertadores
      </span>
      <span class="legend-item">
        <span class="legend-dot sudamericana"></span>Copa Sudamericana
      </span>
      <span class="legend-item">
        <span class="legend-dot descenso"></span>Descenso
      </span>
    `;
    fragment.appendChild(legend);

    return fragment;
  }

  // -------------------------------------------------------------------------
  // Renderizado de fixtures (partidos)
  // -------------------------------------------------------------------------

  /**
   * @param {Object} attrs - atributos del sensor
   * @returns {DocumentFragment}
   */
  _renderFixtures(attrs) {
    const fragment = document.createDocumentFragment();
    const partidos = attrs.partidos;

    if (!Array.isArray(partidos) || partidos.length === 0) {
      const div = document.createElement("div");
      div.className = "no-data";
      div.textContent = "No hay partidos programados para este período.";
      fragment.appendChild(div);
      return fragment;
    }

    // Agrupar por fecha
    /** @type {Map<string, Array>} */
    const byDate = new Map();
    for (const partido of partidos) {
      const fecha = partido.fecha || "Sin fecha";
      if (!byDate.has(fecha)) byDate.set(fecha, []);
      byDate.get(fecha).push(partido);
    }

    for (const [fecha, matches] of byDate) {
      // Header de fecha
      const dateHeader = document.createElement("div");
      dateHeader.className = "fixture-date-header";
      dateHeader.textContent = formatDateLabel(fecha);
      fragment.appendChild(dateHeader);

      // Grupo de partidos de esa fecha
      const group = document.createElement("div");
      group.className = "fixture-date-group";

      for (const m of matches) {
        const row = this._buildFixtureRow(m);
        group.appendChild(row);
      }

      fragment.appendChild(group);
    }

    // Timestamp de última actualización
    if (attrs.ultima_actualizacion) {
      const ts = document.createElement("div");
      ts.style.cssText = "padding:6px 12px;font-size:0.7rem;color:var(--secondary-text-color);text-align:right;";
      const dt = new Date(attrs.ultima_actualizacion + "Z");
      ts.textContent = `Actualizado: ${dt.toLocaleString("es-CL")}`;
      fragment.appendChild(ts);
    }

    return fragment;
  }

  /**
   * Construir una fila de fixture.
   * @param {Object} m - partido
   * @returns {HTMLElement}
   */
  _buildFixtureRow(m) {
    const row = document.createElement("div");
    row.className = "fixture-row";

    const isFinished = FINISHED_STATES.has(m.estado);
    const isLive = LIVE_STATES.has(m.estado);
    const hasScore = m.goles_local !== null && m.goles_local !== undefined &&
                     m.goles_visita !== null && m.goles_visita !== undefined;

    // Equipo local (derecha)
    const homeDiv = document.createElement("div");
    homeDiv.className = "team-home";
    const homeSpan = document.createElement("span");
    homeSpan.textContent = m.local || "";
    homeDiv.appendChild(homeSpan);
    if (m.logo_local) homeDiv.appendChild(teamLogo(m.logo_local, m.local));

    // Centro (marcador o hora)
    const center = document.createElement("div");
    center.className = "fixture-center";

    const scoreDiv = document.createElement("div");
    if (isFinished || isLive) {
      scoreDiv.className = "fixture-score" + (isLive ? " live" : "");
      scoreDiv.textContent = hasScore ? `${m.goles_local} - ${m.goles_visita}` : "- -";
    } else {
      scoreDiv.className = "fixture-score pending";
      scoreDiv.textContent = m.hora || "TBD";
    }

    const statusDiv = document.createElement("div");
    statusDiv.className = "fixture-status" + (isLive ? " live" : "");
    statusDiv.textContent = isLive ? m.estado : (isFinished ? "Final" : "");

    const jornadaDiv = document.createElement("div");
    jornadaDiv.className = "fixture-jornada";
    jornadaDiv.textContent = m.jornada || "";

    center.appendChild(scoreDiv);
    if (statusDiv.textContent) center.appendChild(statusDiv);
    if (jornadaDiv.textContent) center.appendChild(jornadaDiv);

    // Equipo visita (izquierda)
    const awayDiv = document.createElement("div");
    awayDiv.className = "team-away";
    if (m.logo_visita) awayDiv.appendChild(teamLogo(m.logo_visita, m.visita));
    const awaySpan = document.createElement("span");
    awaySpan.textContent = m.visita || "";
    awayDiv.appendChild(awaySpan);

    row.appendChild(homeDiv);
    row.appendChild(center);
    row.appendChild(awayDiv);

    return row;
  }

  // -------------------------------------------------------------------------
  // Editor visual (panel de configuración de tarjetas en HA)
  // -------------------------------------------------------------------------

  /** Retorna el elemento editor para la UI visual de Lovelace. */
  static getConfigElement() {
    return document.createElement("liga-chile-card-editor");
  }

  /** Configuración de ejemplo para el stub en el panel de tarjetas. */
  static getStubConfig() {
    return {
      entity: "sensor.primera_a_tabla",
      card_type: "tabla",
      title: "Primera A — Tabla de posiciones",
    };
  }

  /** Altura estimada de la tarjeta (en filas de grid de HA). */
  getCardSize() {
    const config = this._config;
    if (!config) return 3;
    return config.card_type === "tabla" ? 9 : 6;
  }
}

// ---------------------------------------------------------------------------
// Editor visual simple (para el panel de configuración de tarjetas en HA)
// ---------------------------------------------------------------------------

class LigaChileCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  get _entityValue() { return this._config.entity || ""; }
  get _cardTypeValue() { return this._config.card_type || "tabla"; }
  get _titleValue() { return this._config.title || ""; }

  _render() {
    const shadow = this.shadowRoot;
    shadow.innerHTML = `
      <style>
        .editor-row {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 12px;
        }
        label { font-size: 0.85rem; color: var(--secondary-text-color); }
        input, select {
          width: 100%;
          padding: 8px;
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 4px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
          font-size: 0.9rem;
          box-sizing: border-box;
        }
      </style>
      <div class="editor-row">
        <div>
          <label>Entidad (sensor)</label>
          <input id="entity" type="text" value="${esc(this._entityValue)}"
                 placeholder="sensor.primera_a_tabla" />
        </div>
        <div>
          <label>Tipo de tarjeta</label>
          <select id="card_type">
            <option value="tabla" ${this._cardTypeValue === "tabla" ? "selected" : ""}>Tabla de posiciones</option>
            <option value="fixtures" ${this._cardTypeValue === "fixtures" ? "selected" : ""}>Partidos / Fixtures</option>
          </select>
        </div>
        <div>
          <label>Título (opcional)</label>
          <input id="title" type="text" value="${esc(this._titleValue)}"
                 placeholder="Título personalizado" />
        </div>
      </div>
    `;

    shadow.querySelector("#entity").addEventListener("change", (e) => {
      this._fireConfigChanged({ entity: e.target.value.trim() });
    });
    shadow.querySelector("#card_type").addEventListener("change", (e) => {
      this._fireConfigChanged({ card_type: e.target.value });
    });
    shadow.querySelector("#title").addEventListener("change", (e) => {
      this._fireConfigChanged({ title: e.target.value.trim() || undefined });
    });
  }

  _fireConfigChanged(partial) {
    this._config = { ...this._config, ...partial };
    // Eliminar claves undefined
    for (const key of Object.keys(this._config)) {
      if (this._config[key] === undefined) delete this._config[key];
    }
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config: this._config } })
    );
  }
}

// ---------------------------------------------------------------------------
// Registro de custom elements
// ---------------------------------------------------------------------------

customElements.define("liga-chile-card", LigaChileCard);
customElements.define("liga-chile-card-editor", LigaChileCardEditor);

// Registro en el window para que HA detecte la tarjeta en el panel
window.customCards = window.customCards || [];
window.customCards.push({
  type: "liga-chile-card",
  name: "Liga Chile Card",
  description: "Tabla de posiciones y fixtures de la Primera A y Primera B del fútbol chileno.",
  preview: true,
  documentationURL: "https://github.com/drimtek/liga_chile",
});
