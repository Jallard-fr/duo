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

// [clé, libellé, émoticône, intensité 0-4]
const MOODS = [
  ["pas_ce_soir", "Pas ce soir", "\u{1F634}", 0],
  ["douceur", "Envie de douceur", "\u{1F497}", 1],
  ["curieux", "Curieux(se)", "\u{1F60F}", 2],
  ["nouveaute", "Envie de nouveauté", "\u{2728}", 3],
  ["torride", "Envie de torride", "\u{1F525}", 4],
];

const MOOD_NOVELTY = "nouveaute";
const NEW_IDEA_UNKNOWN = "__unknown__";
const MAX_INTENSITY = 4;

function moodInfo(key) {
  return MOODS.find(([k]) => k === key) || MOODS[0];
}

function gauge(level) {
  return "\u2764\uFE0F".repeat(level) + "\u{1F90D}".repeat(MAX_INTENSITY - level);
}

function esc(value) {
  return String(value == null ? "" : value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

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
  ["evening_entity", "Entité soirée"],
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
    config.evening_entity = find(
      (id) => id.startsWith("sensor.duo_") && id.endsWith("_evening")
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
    // Ne pas reconstruire le DOM pendant que l'on remplit le panneau
    // « ce soir » : cela ferait perdre le focus et la saisie en cours.
    if (this._draft && this._draft.open) return;
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

  // --- Section « ce soir » -------------------------------------------------

  _eveningData() {
    const cfg = this._config;
    const hass = this._hass;
    const entity = cfg.evening_entity ? hass.states[cfg.evening_entity] : null;
    const attrs = entity ? entity.attributes || {} : {};
    const states = attrs.states || {};
    const myUserId = hass.user ? hass.user.id : null;

    let me = null;
    Object.keys(states).forEach((name) => {
      if (states[name].user_id && states[name].user_id === myUserId) me = name;
    });
    // Aucune association configurée : on laisse le contrôle au partenaire 1
    // pour rester utilisable comme avant.
    if (!me && attrs.mapping_configured === false) me = cfg.partner1;

    const other = me
      ? me === cfg.partner1
        ? cfg.partner2
        : cfg.partner1
      : null;

    return {
      available: !!entity,
      states,
      accessories: attrs.available_accessories || [],
      mapped: attrs.mapping_configured !== false,
      me,
      other,
    };
  }

  _renderPartnerBox(name, state, isMe) {
    if (!state) return "";
    const level = state.intensity || 0;
    const acc = state.accessories || [];
    const idea = state.new_idea_label;
    const updated = state.updated
      ? new Date(state.updated).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      : null;
    return `
      <div class="partner-box">
        <div class="partner-head">${state.emoji || ""} ${esc(name)}${isMe ? " (toi)" : ""}</div>
        <div>${esc(state.mood_label || "")}</div>
        <div class="gauge">${gauge(level)}</div>
        ${acc.length ? `<div class="meta">\u{1F9FA} Accessoires : ${esc(acc.join(", "))}</div>` : ""}
        ${idea ? `<div class="meta">\u2728 ${esc(idea)}</div>` : ""}
        ${updated ? `<div class="meta">Mis à jour à ${updated}</div>` : ""}
      </div>
    `;
  }

  _renderDraft(data) {
    const draft = this._draft;
    const [key, label, emoji, level] = moodInfo(draft.mood);
    const accessories = data.accessories;

    return `
      <div class="draft">
        <h4>${emoji} ${esc(label)} ${gauge(level)}</h4>
        ${
          accessories.length
            ? `<div class="note">Accessoires que tu aimerais utiliser ce soir :</div>
               <div class="chips">
                 ${accessories
                   .map(
                     (a) =>
                       `<button class="chip ${draft.accessories.includes(a) ? "on" : ""}" data-accessory="${esc(a)}">${esc(a)}</button>`
                   )
                   .join("")}
               </div>`
            : `<div class="note">Aucun accessoire enregistré pour l'instant (voir « Préférences &amp; accessoires » plus bas).</div>`
        }
        ${
          key === MOOD_NOVELTY
            ? `<div class="note">Tu as quelque chose de nouveau en tête ?</div>
               <input type="text" id="newIdea" placeholder="Une envie, une idée à tester..."
                      value="${esc(draft.unknown ? "" : draft.newIdea)}" ${draft.unknown ? "disabled" : ""} />
               <div class="chips">
                 <button class="chip ${draft.unknown ? "on" : ""}" id="unknownIdea">\u{1F937} Je ne sais pas vraiment</button>
               </div>`
            : ""
        }
        <div class="actions">
          <button id="sendMood">Envoyer à ${esc(data.other || "mon/ma partenaire")}</button>
          <button class="secondary" id="cancelMood">Annuler</button>
        </div>
      </div>
    `;
  }

  _renderTonight() {
    const cfg = this._config;
    const data = this._eveningData();

    if (!data.available) {
      return `<div class="section"><h3>Ce soir</h3>
        <div class="note">Ajoute l'entité « Soirée » (<code>sensor.…_evening</code>)
        dans la configuration de la carte.</div></div>`;
    }

    if (!data.me) {
      return `<div class="section"><h3>Ce soir</h3>
        ${this._renderPartnerBox(cfg.partner1, data.states[cfg.partner1], false)}
        ${this._renderPartnerBox(cfg.partner2, data.states[cfg.partner2], false)}
        <div class="note">Ton compte Home Assistant n'est associé à aucun partenaire.
        Renseigne-le dans les options de l'intégration Duo.</div></div>`;
    }

    const draftOpen = this._draft && this._draft.open;

    return `
      <div class="section">
        <h3>Ce soir</h3>
        ${this._renderPartnerBox(data.other, data.states[data.other], false)}
        ${this._renderPartnerBox(data.me, data.states[data.me], true)}
        ${
          draftOpen
            ? this._renderDraft(data)
            : `<div class="note">Ton humeur :</div>
               <div class="moods">
                 ${MOODS.map(
                   ([k, l, e]) =>
                     `<button class="mood-btn ${
                       data.states[data.me] && data.states[data.me].mood === k
                         ? "active"
                         : ""
                     }" data-mood="${k}">
                        <span class="emo">${e}</span><span>${esc(l)}</span>
                      </button>`
                 ).join("")}
               </div>`
        }
      </div>
    `;
  }

  _attachTonightEvents() {
    const root = this._root;
    const data = this._eveningData();
    if (!data.me) return;

    root.querySelectorAll(".mood-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const state = data.states[data.me] || {};
        this._draft = {
          open: true,
          mood: btn.dataset.mood,
          accessories: [...(state.accessories || [])],
          newIdea: state.new_idea && state.new_idea !== NEW_IDEA_UNKNOWN ? state.new_idea : "",
          unknown: state.new_idea === NEW_IDEA_UNKNOWN,
        };
        this._render();
      });
    });

    if (!this._draft || !this._draft.open) return;

    root.querySelectorAll("[data-accessory]").forEach((chip) => {
      chip.addEventListener("click", () => {
        const value = chip.dataset.accessory;
        const list = this._draft.accessories;
        const idx = list.indexOf(value);
        if (idx >= 0) list.splice(idx, 1);
        else list.push(value);
        chip.classList.toggle("on");
      });
    });

    const ideaInput = root.getElementById("newIdea");
    if (ideaInput) {
      ideaInput.addEventListener("input", () => {
        this._draft.newIdea = ideaInput.value;
      });
    }

    const unknownBtn = root.getElementById("unknownIdea");
    if (unknownBtn) {
      unknownBtn.addEventListener("click", () => {
        this._draft.unknown = !this._draft.unknown;
        if (this._draft.unknown) this._draft.newIdea = "";
        const wasOpen = this._draft.open;
        this._draft.open = false;
        this._render();
        this._draft.open = wasOpen;
        this._render();
      });
    }

    const cancelBtn = root.getElementById("cancelMood");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        this._draft = null;
        this._render();
      });
    }

    const sendBtn = root.getElementById("sendMood");
    if (sendBtn) {
      sendBtn.addEventListener("click", () => {
        const draft = this._draft;
        let newIdea = null;
        if (draft.mood === MOOD_NOVELTY) {
          newIdea = draft.unknown
            ? NEW_IDEA_UNKNOWN
            : draft.newIdea.trim() || NEW_IDEA_UNKNOWN;
        }
        this._duoService("set_mood", {
          partner: data.me,
          mood: draft.mood,
          accessories: draft.accessories,
          new_idea: newIdea,
        });
        this._draft = null;
        this._render();
      });
    }
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
        .moods { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
        .mood-btn {
          flex: 1 1 auto; min-width: 84px; display: flex; flex-direction: column;
          align-items: center; gap: 2px; padding: 8px 6px; border-radius: 10px;
          border: 1px solid var(--divider-color, #ccc); background: transparent;
          color: var(--primary-text-color, inherit); font-weight: 500; font-size: 0.8em;
        }
        .mood-btn .emo { font-size: 1.5em; line-height: 1; }
        .mood-btn.active { border-color: var(--primary-color, #e91e63); border-width: 2px; }
        .partner-box {
          border: 1px solid var(--divider-color, #ccc); border-radius: 10px;
          padding: 10px; margin-bottom: 10px;
        }
        .partner-head { font-weight: 700; margin-bottom: 2px; }
        .gauge { letter-spacing: 2px; margin-bottom: 4px; }
        .draft {
          border: 2px solid var(--primary-color, #e91e63); border-radius: 10px;
          padding: 12px; margin-bottom: 10px;
        }
        .draft h4 { margin: 0 0 8px 0; }
        .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
        .chip {
          border: 1px solid var(--divider-color, #ccc); border-radius: 16px;
          padding: 5px 11px; font-size: 0.85em; background: transparent;
          color: var(--primary-text-color, inherit); font-weight: 500;
        }
        .chip.on { background: var(--primary-color, #e91e63); color: white; border-color: transparent; }
        .draft input[type="text"] { width: 100%; box-sizing: border-box; margin-bottom: 8px; padding: 8px; }
        .note { font-size: 0.85em; opacity: 0.7; }
      </style>
      <ha-card>
        <div class="title">💞 Duo — ${cfg.partner1} &amp; ${cfg.partner2}</div>

        ${this._renderTonight()}

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
            <input type="text" id="accessories" placeholder=