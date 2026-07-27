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

class DuoCard extends HTMLElement {
  setConfig(config) {
    if (!config.entry_id) {
      throw new Error("duo-card: 'entry_id' est obligatoire.");
    }
    if (!config.partner1 || !config.partner2) {
      throw new Error("duo-card: 'partner1' et 'partner2' sont obligatoires.");
    }
    if (!config.suggestion_entity || !config.timer_entity) {
      throw new Error(
        "duo-card: 'suggestion_entity' et 'timer_entity' sont obligatoires."
      );
    }
    this._config = config;
    if (!this._root) {
      this._root = this.attachShadow({ mode: "open" });
    }
    this._render();
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

customElements.define("duo-card", DuoCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "duo-card",
  name: "Duo - Intimité de couple",
  description: "Carte textuelle pour piloter l'application d'intimité de couple Duo.",
});
