// Duo - carte Lovelace pour l'intégration Home Assistant "duo".
// Carte 100% textuelle : aucune image, aucune description explicite d'acte.
// Le contenu affiché reste au niveau des attributs exposés par l'intégration
// (nom d'activité suggestif, catégorie, intensité, durée, accessoire).

const CATEGORIES = [
  ["preliminaires", "Préliminaires"],
  ["sensoriel", "Sensoriel"],
  ["massage", "Massage"],
  ["jeu_de_role", "Jeu de rôle"],
  ["communication", "Communication & Fantasmes"],
  ["intensite_plus", "Intensité +"],
];

const MOODS = [
  ["pas_ce_soir", "Pas ce soir"],
  ["douceur", "Envie de douceur"],
  ["curieux", "Curieux(se)"],
  ["nouveaute", "Envie de nouveauté"],
  ["torride", "Envie de torride"],
];

function fmtTime(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds || 0));
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

const REQUIRED_FIELDS = [
  ["entry_id", "Configuration Duo"],
  ["partner1", "Prénom du partenaire 1"],
  ["partner2", "Prénom du partenaire 2"],
  ["suggestion_entity", "Entité suggestion"],
  ["timer_entity", "Entité minuteur"],
];

function titleCase(value) {
  if (!value) return "";
  return value
    .split("_")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

class DuoCard extends HTMLElement {
  // --- Éditeur visuel ------------------------------------------------------
  static getConfigElement() {
    return document.createElement("duo-card-editor");
  }

  // Pré-remplit la carte à l'ajout depuis le sélecteur graphique.
  static async getStubConfig(hass) {
    const config = { type: "custom:duo-card" };
    const ids = Object.keys(hass.states || {});
    const find = (fn) => ids.find(fn) || "";

    config.suggestion_entity = find(
      (id) => id.startsWith("sensor.duo_") && id.endsWith("_current_suggestion")
    );
    config.timer_entity = find(
      (id) => id.startsWith("sensor.duo_") && id.endsWith("_timer")
    );
    config.history_entity = find(
      (id) => id.startsWith("sensor.duo_") && id.endsWith("_history")
    );

    const moods = ids.filter((id) => id.startsWith("select.duo_mood_"));
    config.mood_entity_partner1 = moods[0] || "";
    config.mood_entity_partner2 = moods[1] || "";
    config.partner1 = titleCase((moods[0] || "").replace("select.duo_mood_", ""));
    config.partner2 = titleCase((moods[1] || "").replace("select.duo_mood_", ""));

    try {
      const entries = await hass.callWS({
        type: "config_entries/get",
        domain: "duo",
      });
      const duoEntries = (entries || []).filter((e) => e.domain === "duo");
      if (duoEntries.length) config.entry_id = duoEntries[0].entry_id;
    } catch (err) {
      // L'utilisateur n'est peut-être pas administrateur : champ à saisir.
    }

    return config;
  }

  setConfig(config) {
    this._config = config || {};
    if (!this._root) {
      this._root = this.attachShadow({ mode: "open" });
    }
    this._render();
  }

  _missingFields() {
    return REQUIRED_FIELDS.filter(([key]) => !this._config[key]);
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 8;
  }

  _callService(domain, service, data) {
    this._hass.callService(domain, service, data);
  }

  _duoService(service, extra) {
    this._callService("duo", service, {
      entry_id: this._config.entry_id,
      ...extra,
    });
  }

  _render() {
    if (!this._root || !this._hass || !this._config) return;

    const missing = this._missingFields();
    if (missing.length) {
      this._root.innerHTML = `
        <style>
          ha-card { padding: 16px; }
          .todo { font-weight: 600; margin-bottom: 8px; }
          ul { margin: 0; padding-left: 20px; opacity: 0.8; }
        </style>
        <ha-card>
          <div class="todo">💞 Duo — configuration à compléter</div>
          <ul>${missing.map(([, label]) => `<li>${label}</li>`).join("")}</ul>
        </ha-card>
      `;
      return;
    }

    const cfg = this._config;
    const hass = this._hass;
    const suggestion = hass.states[cfg.suggestion_entity];
    const timer = hass.states[cfg.timer_entity];
    const history = cfg.history_entity ? hass.states[cfg.history_entity] : null;

    const status = suggestion ? suggestion.attributes.status || "idle" : "idle";
    const running = timer ? timer.attributes.running : false;
    const remaining = timer ? Number(timer.state) : 0;
    const total = timer ? timer.attributes.total_seconds || 1 : 1;
    const progressPct = Math.round((1 - remaining / Math.max(total, 1)) * 100);

    this._root.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 16px; font-family: var(--paper-font-body1_-_font-family, inherit); }
        .title { font-size: 1.2em; font-weight: 600; margin-bottom: 12px; }
        .section { margin-bottom: 20px; }
        .section h3 { margin: 0 0 8px 0; font-size: 1em; opacity: 0.8; }
        .row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; gap: 8px; }
        .row label { flex: 1; }
        select, input[type="text"] { flex: 1; padding: 4px; }
        button {
          border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer;
          background: var(--primary-color, #e91e63); color: white; font-weight: 600;
        }
        button.secondary { background: var(--secondary-background-color, #888); }
        button:disabled { opacity: 0.4; cursor: not-allowed; }
        .suggestion-box {
          border: 1px solid var(--divider-color, #ccc); border-radius: 10px;
          padding: 12px; margin-bottom: 10px;
        }
        .suggestion-name { font-size: 1.1em; font-weight: 700; margin-bottom: 4px; }
        .suggestion-desc { opacity: 0.85; margin-bottom: 8px; }
        .meta { font-size: 0.85em; opacity: 0.7; margin-bottom: 8px; }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .progress-outer {
          background: var(--divider-color, #ddd); border-radius: 6px; height: 10px; overflow: hidden; margin: 8px 0;
        }
        .progress-inner { background: var(--primary-color, #e91e63); height: 100%; }
        .reminder { font-size: 0.8em; opacity: 0.6; font-style: italic; margin-top: 6px; }
        .history-item { font-size: 0.85em; opacity: 0.8; padding: 2px 0; }
        details summary { cursor: pointer; opacity: 0.8; margin-bottom: 8px; }
        .pref-row { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 8px; margin-bottom: 4px; }
      </style>
      <ha-card>
        <div class="title">💞 Duo — ${cfg.partner1} &amp; ${cfg.partner2}</div>

        <div class="section">
          <h3>Ce soir</h3>
          <div class="row">
            <label>${cfg.partner1}</label>
            <select id="mood1">
              ${MOODS.map(
                ([k, l]) => `<option value="${k}">${l}</option>`
              ).join("")}
            </select>
          </div>
          <div class="row">
            <label>${cfg.partner2}</label>
            <select id="mood2">
              ${MOODS.map(
                ([k, l]) => `<option value="${k}">${l}</option>`
              ).join("")}
            </select>
          </div>
        </div>

        <div class="section">
          <h3>Suggestion</h3>
          ${
            suggestion && suggestion.attributes.description
              ? `
            <div class="suggestion-box">
              <div class="suggestion-name">${suggestion.state}</div>
              <div class="suggestion-desc">${suggestion.attributes.description}</div>
              <div class="meta">
                Catégorie : ${suggestion.attributes.category || "-"} ·
                Intensité : ${"♥".repeat(suggestion.attributes.intensity || 0)}${"♡".repeat(5 - (suggestion.attributes.intensity || 0))} ·
                Durée : ${suggestion.attributes.duration_min}-${suggestion.attributes.duration_max} min
                ${suggestion.attributes.accessory ? ` · Accessoire : ${suggestion.attributes.accessory}` : ""}
              </div>
              <div class="meta">Au tour de : <strong>${suggestion.attributes.turn || "-"}</strong> · Statut : ${status}</div>
              <div class="actions">
                ${
                  status === "proposed"
                    ? `<button id="accept">J'accepte</button><button class="secondary" id="decline">Je décline</button>`
                    : ""
                }
              </div>
              <div class="reminder">${suggestion.attributes.reminder || "Chacun peut refuser à tout moment, sans justification."}</div>
            </div>
          `
              : `<div class="suggestion-box">Aucune suggestion pour le moment.</div>`
          }
          <div class="actions">
            <button id="request">Proposer une activité</button>
            <button class="secondary" id="reset">Réinitialiser</button>
          </div>
        </div>

        <div class="section">
          <h3>Minuteur</h3>
          <div>${fmtTime(remaining)} ${running ? "⏳" : ""}</div>
          <div class="progress-outer"><div class="progress-inner" style="width:${running ? progressPct : 0}%"></div></div>
          <div class="actions">
            <button id="stopTimer" ${running ? "" : "disabled"}>Arrêter le minuteur</button>
          </div>
        </div>

        <details class="section">
          <summary>Préférences &amp; accessoires</summary>
          <h3>Préférences de ${cfg.partner1}</h3>
          ${CATEGORIES.map(
            ([k, l]) => `
            <div class="pref-row">
              <label>${l}</label>
              <input type="range" min="0" max="5" step="1" data-partner="1" data-category="${k}" class="pref-slider" />
            </div>
          `
          ).join("")}
          <h3>Préférences de ${cfg.partner2}</h3>
          ${CATEGORIES.map(
            ([k, l]) => `
            <div class="pref-row">
              <label>${l}</label>
              <input type="range" min="0" max="5" step="1" data-partner="2" data-category="${k}" class="pref-slider" />
            </div>
          `
          ).join("")}
          <h3>Accessoires disponibles</h3>
          <div class="row">
            <input type="text" id="accessories" placeholder="bandeau, plume, huile de massage, ..." />
            <button id="saveAccessories">Enregistrer</button>
          </div>
        </details>

        ${
          history && history.attributes.last_entries && history.attributes.last_entries.length
            ? `
          <details class="section">
            <summary>Historique récent</summary>
            ${history.attributes.last_entries
              .slice()
              .reverse()
              .map(
                (h) =>
                  `<div class="history-item">${h.turn || "-"} · ${h.name} · ${h.response}</div>`
              )
              .join("")}
          </details>
        `
            : ""
        }
      </ha-card>
    `;

    this._attachEvents();
  }

  _attachEvents() {
    const root = this._root;
    const cfg = this._config;

    const mood1 = root.getElementById("mood1");
    const mood2 = root.getElementById("mood2");
    if (mood1) {
      const current = this._hass.states[cfg.mood_entity_partner1];
      if (current) {
        const key = MOODS.find(([, label]) => label === current.state);
        if (key) mood1.value = key[0];
      }
      mood1.addEventListener("change", () =>
        this._duoService("set_mood", { partner: cfg.partner1, mood: mood1.value })
      );
    }
    if (mood2) {
      const current = this._hass.states[cfg.mood_entity_partner2];
      if (current) {
        const key = MOODS.find(([, label]) => label === current.state);
        if (key) mood2.value = key[0];
      }
      mood2.addEventListener("change", () =>
        this._duoService("set_mood", { partner: cfg.partner2, mood: mood2.value })
      );
    }

    const requestBtn = root.getElementById("request");
    if (requestBtn) requestBtn.addEventListener("click", () => this._duoService("request_suggestion", {}));

    const acceptBtn = root.getElementById("accept");
    if (acceptBtn)
      acceptBtn.addEventListener("click", () =>
        this._duoService("respond_suggestion", { response: "accepted" })
      );

    const declineBtn = root.getElementById("decline");
    if (declineBtn)
      declineBtn.addEventListener("click", () =>
        this._duoService("respond_suggestion", { response: "declined" })
      );

    const resetBtn = root.getElementById("reset");
    if (resetBtn) resetBtn.addEventListener("click", () => this._duoService("reset_session", {}));

    const stopTimerBtn = root.getElementById("stopTimer");
    if (stopTimerBtn) stopTimerBtn.addEventListener("click", () => this._duoService("stop_timer", {}));

    const saveAccessoriesBtn = root.getElementById("saveAccessories");
    if (saveAccessoriesBtn) {
      saveAccessoriesBtn.addEventListener("click", () => {
        const input = root.getElementById("accessories");
        const accessories = input.value
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        this._duoService("set_accessories", { accessories });
      });
    }

    root.querySelectorAll(".pref-slider").forEach((slider) => {
      slider.addEventListener("change", () => {
        const partnerName = slider.dataset.partner === "1" ? cfg.partner1 : cfg.partner2;
        this._duoService("set_preference", {
          partner: partnerName,
          category: slider.dataset.category,
          rating: Number(slider.value),
        });
      });
    });
  }
}

// ---------------------------------------------------------------------------
// Éditeur visuel de la carte (formulaire natif Home Assistant)
// ---------------------------------------------------------------------------

const EDITOR_LABELS = {
  entry_id: "Configuration Duo",
  partner1: "Prénom du partenaire 1",
  partner2: "Prénom du partenaire 2",
  suggestion_entity: "Entité suggestion",
  timer_entity: "Entité minuteur",
  history_entity: "Entité historique (facultatif)",
  mood_entity_partner1: "Humeur du partenaire 1 (facultatif)",
  mood_entity_partner2: "Humeur du partenaire 2 (facultatif)",
};

class DuoCardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._entries = [];
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._entriesRequested) {
      this._entriesRequested = true;
      this._loadEntries();
    }
    this._render();
  }

  async _loadEntries() {
    try {
      const entries = await this._hass.callWS({
        type: "config_entries/get",
        domain: "duo",
      });
      this._entries = (entries || [])
        .filter((e) => e.domain === "duo")
        .map((e) => ({ value: e.entry_id, label: e.title || e.entry_id }));
    } catch (err) {
      this._entries = [];
    }
    this._render();
  }

  _schema() {
    const entryField = this._entries.length
      ? {
          name: "entry_id",
          required: true,
          selector: { select: { options: this._entries, mode: "dropdown" } },
        }
      : { name: "entry_id", required: true, selector: { text: {} } };

    const sensor = { entity: { domain: "sensor", integration: "duo" } };
    const select = { entity: { domain: "select", integration: "duo" } };

    return [
      entryField,
      { name: "partner1", required: true, selector: { text: {} } },
      { name: "partner2", required: true, selector: { text: {} } },
      { name: "suggestion_entity", required: true, selector: sensor },
      { name: "timer_entity", required: true, selector: sensor },
      { name: "history_entity", selector: sensor },
      { name: "mood_entity_partner1", selector: select },
      { name: "mood_entity_partner2", selector: select },
    ];
  }

  _render() {
    if (!this._hass) return;

    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) =>
        EDITOR_LABELS[schema.name] || schema.name;
      this._form.addEventListener("value-changed", (ev) => {
        ev.stopPropagation();
        this._config = { type: "custom:duo-card", ...ev.detail.value };
        this.dispatchEvent(
          new CustomEvent("config-changed", {
            detail: { config: this._config },
            bubbles: true,
            composed: true,
          })
        );
      });
      this.appendChild(this._form);
    }

    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = this._config;
  }
}

customElements.define("duo-card", DuoCard);
customElements.define("duo-card-editor", DuoCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "duo-card",
  name: "Duo - Intimité de couple",
  description: "Carte textuelle pour piloter l'application d'intimité de couple Duo.",
  preview: true,
  documentationURL: "https://github.com/Jallard-fr/duo",
});
