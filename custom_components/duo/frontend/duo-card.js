// Duo - carte Lovelace pour l'intégration Home Assistant "duo".
// Carte 100% textuelle : aucune image, aucune description explicite d'acte.
// Le contenu affiché reste au niveau des attributs exposés par l'intégration
// (nom d'activité suggestif, catégorie, intensité, durée, accessoire).

// Phases temporelles d'un rapport (voir PHASE_* dans const.py, inspiré du
// modèle de Masters & Johnson complété par Kaplan) : encore habillés et
// début de stimulation (Excitation), contacts avec les zones érogènes
// (Préliminaires), pénétration intense (Intense), puis tendresse après
// (Résolution).
const PHASES = [
  ["", "Niveau en cours (progression guidée)"],
  ["phase_excitation", "Excitation"],
  ["phase_preliminaires", "Préliminaires"],
  ["phase_intense", "Intense"],
  ["phase_resolution", "Résolution"],
];

const CATEGORIES = [
  ["preliminaires", "Préliminaires"],
  ["sensoriel", "Sensoriel"],
  ["massage", "Massage"],
  ["jeu_de_role", "Jeu de rôle"],
  ["communication", "Communication & Fantasmes"],
  ["intensite_plus", "Intensité +"],
  ["resolution", "Tendresse & après"],
];

// Choix fermés proposés par le questionnaire de préférences, par catégorie.
const QUIZ_CHOICES = [
  ["0", "Jamais", 0],
  ["2", "Parfois", 2],
  ["4", "Souvent", 4],
  ["5", "Toujours", 5],
];

// Questionnaire de limites : questions fermées et explicites, groupées par
// pratique (voir PRACTICE_* dans const.py). "donne"/"recoit" distingue le
// rôle actif du rôle passif ; "usage" (jouets) est symétrique. Le libellé
// de la stimulation orale s'adapte au sexe concerné (fellation/cunnilingus)
// quand il est connu, sinon reste générique.
function oralLabel(sex) {
  if (sex === "Homme") return "une fellation";
  if (sex === "Femme") return "un cunnilingus";
  return "une stimulation orale";
}

const PRACTICE_GROUPS = [
  {
    key: "oral",
    label: "Stimulation orale",
    questions: [
      {
        role: "donne",
        text: (mySex, otherSex) => `Acceptes-tu de faire ${oralLabel(otherSex)} à ton/ta partenaire ?`,
      },
      {
        role: "recoit",
        text: (mySex) => `Acceptes-tu que ton/ta partenaire te fasse ${oralLabel(mySex)} ?`,
      },
    ],
  },
  {
    key: "anal",
    label: "Pénétration anale (sodomie)",
    questions: [
      { role: "donne", text: () => "Acceptes-tu de pratiquer une pénétration anale sur ton/ta partenaire ?" },
      { role: "recoit", text: () => "Acceptes-tu de recevoir une pénétration anale ?" },
    ],
  },
  {
    key: "discipline",
    label: "Discipline légère (fessée, fouet léger)",
    questions: [
      { role: "donne", text: () => "Acceptes-tu d'appliquer une discipline légère à ton/ta partenaire ?" },
      { role: "recoit", text: () => "Acceptes-tu de la recevoir ?" },
    ],
  },
  {
    key: "liens",
    label: "Contrainte douce / liens",
    questions: [
      { role: "donne", text: () => "Acceptes-tu d'attacher ton/ta partenaire avec des liens doux ?" },
      { role: "recoit", text: () => "Acceptes-tu d'être attaché(e) ?" },
    ],
  },
  {
    key: "jouets",
    label: "Jouets vibrants",
    questions: [
      { role: "usage", text: () => "Acceptes-tu l'utilisation de jouets/accessoires vibrants à deux ?" },
    ],
  },
];

const PRACTICE_ANSWER_CHOICES = [
  ["oui", "Oui"],
  ["a_voir", "À voir"],
  ["non", "Non"],
];

function flattenPracticeSteps() {
  const steps = [];
  PRACTICE_GROUPS.forEach((group) => {
    group.questions.forEach((question) => {
      steps.push({
        groupKey: group.key,
        groupLabel: group.label,
        role: question.role,
        text: question.text,
      });
    });
  });
  return steps;
}

// Questionnaire de postures : contrairement au questionnaire de limites, la
// question porte toujours sur la posture dans laquelle on REÇOIT quelque
// chose (une caresse, une fessée à quatre pattes, par exemple), jamais sur
// celle de qui agit — voir POSITION_* dans const.py.
const POSITION_QUESTIONS = [
  ["position_allonge", "Allongé(e)", "en étant allongé(e)"],
  ["position_quatre_pattes", "À quatre pattes", "en étant à quatre pattes"],
  [
    "position_penche_avant",
    "Penché(e) en avant",
    "en étant penché(e) en avant, appuyé(e) sur un meuble ou un mur",
  ],
  ["position_debout", "Debout", "en étant debout"],
  ["position_assis", "Assis(e)", "en étant assis(e), sur une chaise ou le bord du lit"],
  ["position_genoux", "À genoux", "en étant à genoux"],
];

// Catalogue d'accessoires : lu dynamiquement depuis les attributs de
// l'entité "soirée" (accessory_catalog / accessory_categories), exposés par
// l'intégration à partir de custom_components/duo/accessories.py, qui reste
// la seule source de vérité — la carte n'en garde pas sa propre copie.
let ACCESSORY_CATALOG = [];
let ACCESSORY_CATEGORIES = [];

function syncAccessoryCatalog(evAttrs) {
  if (Array.isArray(evAttrs.accessory_catalog)) {
    ACCESSORY_CATALOG = evAttrs.accessory_catalog;
  }
  if (Array.isArray(evAttrs.accessory_categories)) {
    ACCESSORY_CATEGORIES = evAttrs.accessory_categories.map((c) => [c.key, c.label]);
  }
}

// [clé, libellé, émoticône, intensité 0-4]
const MOODS = [
  ["pas_ce_soir", "Pas aujourd'hui", "\u{1F634}", 0],
  ["plus_tard", "Peut-être plus tard", "\u{1F552}", 1],
  ["douceur", "Envie de douceur", "\u{1F497}", 1],
  ["curieux", "Curieux(se)", "\u{1F60F}", 2],
  ["nouveaute", "Envie de nouveauté", "\u{2728}", 3],
  ["torride", "Envie de torride", "\u{1F525}", 4],
];

const MOOD_NOVELTY = "nouveaute";
const NEW_IDEA_UNKNOWN = "__unknown__";
const MAX_INTENSITY = 4;

function accessoryLabel(id) {
  const found = ACCESSORY_CATALOG.find((item) => item.id === id);
  return found ? found.label : id;
}

// Petit indice visuel quand un accessoire est associé à un sexe acteur
// et/ou récepteur précis (voir accessories.py), pour comprendre pourquoi
// certaines suggestions ne le proposent pas selon qui agit/reçoit.
function accessorySexHint(item) {
  const parts = [];
  if (item.actor_sex && item.actor_sex !== "indifferent") {
    parts.push(`porté par : ${item.actor_sex}`);
  }
  if (item.receiver_sex && item.receiver_sex !== "indifferent") {
    parts.push(`pour récepteur : ${item.receiver_sex}`);
  }
  return parts.length ? ` (${parts.join(", ")})` : "";
}

// Thèmes visuels de la carte : surchargent localement (dans le shadow DOM
// de la carte uniquement) les variables CSS utilisées par son style. Le
// thème "auto" ne surcharge rien et suit donc le thème Home Assistant actif.
const THEME_OPTIONS = [
  ["auto", "Thème Home Assistant"],
  ["rose", "Romantique"],
  ["sombre", "Nuit"],
  ["elegant", "Élégant"],
  ["doux", "Doux (pastel)"],
  ["amour", "Amour (évolue avec la phase)"],
];

// Thème "Amour" : fond sombre fixe, mais la couleur d'accent évolue avec la
// phase en cours (voir PHASE_* dans const.py) — rose pâle en excitation,
// rose flashy en préliminaires, rouge en intense, bleu en résolution.
const AMOUR_PHASE_COLORS = {
  phase_excitation: "#f4a6c6",
  phase_preliminaires: "#ff2d95",
  phase_intense: "#e0182b",
  phase_resolution: "#5b7fe0",
};

function amourPreset(phase) {
  const primary = AMOUR_PHASE_COLORS[phase] || AMOUR_PHASE_COLORS.phase_preliminaires;
  return {
    "--primary-color": primary,
    "--card-background-color": "#170f13",
    "--ha-card-background": "#170f13",
    "--secondary-background-color": "#241620",
    "--divider-color": "#3d2530",
    "--primary-text-color": "#f7e9ee",
    "--secondary-text-color": "#d1a8b8",
  };
}

const THEME_PRESETS = {
  auto: null,
  rose: {
    "--primary-color": "#e91e63",
    "--card-background-color": "#fff5f8",
    "--ha-card-background": "#fff5f8",
    "--secondary-background-color": "#ffe4ec",
    "--divider-color": "#f3c4d3",
    "--primary-text-color": "#3a1f2b",
    "--secondary-text-color": "#7a4a5c",
  },
  sombre: {
    "--primary-color": "#ff4d79",
    "--card-background-color": "#171318",
    "--ha-card-background": "#171318",
    "--secondary-background-color": "#241f27",
    "--divider-color": "#3a333e",
    "--primary-text-color": "#f5f0f2",
    "--secondary-text-color": "#c9bcc3",
  },
  elegant: {
    "--primary-color": "#c9a24b",
    "--card-background-color": "#14120f",
    "--ha-card-background": "#14120f",
    "--secondary-background-color": "#1e1a14",
    "--divider-color": "#3a321f",
    "--primary-text-color": "#ece2c8",
    "--secondary-text-color": "#c2b791",
  },
  doux: {
    "--primary-color": "#8e7cc3",
    "--card-background-color": "#f7f5ff",
    "--ha-card-background": "#f7f5ff",
    "--secondary-background-color": "#ece7fb",
    "--divider-color": "#dcd3f4",
    "--primary-text-color": "#332d4b",
    "--secondary-text-color": "#655c8a",
  },
  // Valeur réelle non utilisée (voir themeCss) : juste là pour que
  // THEME_PRESETS.hasOwnProperty("amour") reste vrai (stockage du choix).
  amour: {},
};

function themeCss(themeKey, phase) {
  const preset = themeKey === "amour" ? amourPreset(phase) : THEME_PRESETS[themeKey];
  if (!preset) return "";
  const vars = Object.entries(preset)
    .map(([k, v]) => `${k}: ${v};`)
    .join(" ");
  return `:host { ${vars} }`;
}

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
    this._detailsOpen = this._detailsOpen || {};
    this._quiz = this._quiz || { open: false, kind: null, stepIndex: -1, partner: null, answers: {} };
    this._lingerieDraft = this._lingerieDraft || { open: false, partner: null, items: [] };
    if (!this._root) {
      this._root = this.attachShadow({ mode: "open" });
    }
    this._render();
  }

  _missingFields() {
    return REQUIRED_FIELDS.filter(([key]) => !this._config[key]);
  }

  // --- Thème -----------------------------------------------------------
  // Chaque personne qui consulte le tableau de bord peut choisir son propre
  // thème pour cette carte, sans toucher à la configuration YAML : le choix
  // est mémorisé dans le navigateur (par carte, via son entry_id).
  _themeStorageKey() {
    return `duo-card-theme-${this._config.entry_id || "default"}`;
  }

  _themeKey() {
    try {
      const stored = window.localStorage.getItem(this._themeStorageKey());
      if (stored && THEME_PRESETS.hasOwnProperty(stored)) return stored;
    } catch (err) {
      // Stockage indisponible (navigation privée, etc.) : on ignore.
    }
    return this._config.theme && THEME_PRESETS.hasOwnProperty(this._config.theme)
      ? this._config.theme
      : "auto";
  }

  _setThemeKey(themeKey) {
    try {
      window.localStorage.setItem(this._themeStorageKey(), themeKey);
    } catch (err) {
      // Stockage indisponible : le choix ne survivra pas au rechargement.
    }
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._handleTimerTick();
    // Ne pas reconstruire le DOM pendant que l'on remplit le panneau
    // « ce soir » : cela ferait perdre le focus et la saisie en cours.
    if (this._draft && this._draft.open) return;
    if (this._lingerieDraft && this._lingerieDraft.open) return;
    this._render();
  }

  // --- Bips du minuteur --------------------------------------------------

  _soundStorageKey() {
    return `duo-card-sound-muted-${this._config.entry_id || "default"}`;
  }

  _isSoundMuted() {
    try {
      return window.localStorage.getItem(this._soundStorageKey()) === "1";
    } catch (err) {
      return false;
    }
  }

  _setSoundMuted(muted) {
    try {
      window.localStorage.setItem(this._soundStorageKey(), muted ? "1" : "0");
    } catch (err) {
      // Stockage indisponible : la préférence ne survivra pas au rechargement.
    }
    this._render();
  }

  _beep(frequency, durationMs, type = "sine") {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!this._audioCtx) this._audioCtx = new AudioCtx();
      const ctx = this._audioCtx;
      if (ctx.state === "suspended") ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = frequency;
      osc.connect(gain);
      gain.connect(ctx.destination);

      const now = ctx.currentTime;
      const duration = durationMs / 1000;
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.25, now + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
      osc.start(now);
      osc.stop(now + duration + 0.02);
    } catch (err) {
      // La lecture audio peut échouer (contexte suspendu, permissions...) :
      // ça ne doit jamais bloquer le reste de la carte.
    }
  }

  // Bip toutes les 30 secondes, puis un bip différent chaque seconde durant
  // les 10 dernières secondes, et un dernier bip distinct à zéro.
  _handleTimerTick() {
    const cfg = this._config;
    if (!cfg || !cfg.timer_entity || !this._hass) return;
    const timer = this._hass.states[cfg.timer_entity];
    if (!timer) return;

    const running = !!timer.attributes.running;
    if (!running) {
      this._lastBeepSecond = null;
      return;
    }

    const remaining = Number(timer.state);
    if (remaining === this._lastBeepSecond) return;
    this._lastBeepSecond = remaining;

    if (this._isSoundMuted()) return;

    if (remaining === 0) {
      this._beep(660, 400, "sine");
    } else if (remaining <= 10) {
      this._beep(880, 120, "square");
    } else if (remaining % 30 === 0) {
      this._beep(440, 200, "sine");
    }
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
    syncAccessoryCatalog(attrs);
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
      sessionPhase: attrs.session_phase,
      sessionPhaseLabel: attrs.session_phase_label,
      bothEngaged: !!attrs.both_engaged,
    };
  }

  _renderLevelProgress() {
    const cfg = this._config;
    const data = this._eveningData();
    if (!data.available) return "";

    const progressFor = (partner) => {
      const state = data.states[partner] || {};
      const done = state.phase_progress || 0;
      const target = state.phase_target || 3;
      return `${esc(partner)} : ${Math.min(done, target)}/${target}`;
    };

    const realPhases = PHASES.filter(([k]) => k);
    const currentIndex = realPhases.findIndex(([k]) => k === data.sessionPhase);
    const prevPhase = currentIndex > 0 ? realPhases[currentIndex - 1] : null;
    const nextPhase =
      currentIndex >= 0 && currentIndex < realPhases.length - 1 ? realPhases[currentIndex + 1] : null;

    return `
      <div class="section level-progress">
        <h3>Niveau : ${esc(data.sessionPhaseLabel || "-")}</h3>
        <div class="note">${progressFor(cfg.partner1)} · ${progressFor(cfg.partner2)} activités acceptées avant de passer au niveau suivant.</div>
        <div class="actions">
          <button class="secondary" id="prevPhase" data-phase="${prevPhase ? prevPhase[0] : ""}" ${prevPhase ? "" : "disabled"}>
            ${prevPhase ? `◀ ${esc(prevPhase[1])}` : "◀ —"}
          </button>
          <button class="secondary" id="nextPhase" data-phase="${nextPhase ? nextPhase[0] : ""}" ${nextPhase ? "" : "disabled"}>
            ${nextPhase ? `${esc(nextPhase[1])} ▶` : "— ▶"}
          </button>
        </div>
      </div>
    `;
  }

  // --- Questionnaires (choix fermés) ---------------------------------------
  // Chaque questionnaire est verrouillé à une seule personne à la fois : si
  // l'identité du partenaire connecté n'est pas connue (pas de personne HA
  // associée), un écran demande explicitement "qui répond ?" avant la
  // première question, plutôt que de supposer silencieusement qui que ce
  // soit — personne ne doit répondre par erreur au questionnaire de l'autre.

  _partnerSexes() {
    const cfg = this._config;
    const entity = cfg.evening_entity ? this._hass.states[cfg.evening_entity] : null;
    return (entity && entity.attributes && entity.attributes.partner_sex) || {};
  }

  _renderQuizLauncher() {
    return `
      <div class="row">
        <div class="note">Réponds à quelques questions fermées pour affiner ce qui t'est proposé (rejouable à tout moment). Chacun ne voit et ne répond qu'à son propre questionnaire.</div>
      </div>
      <div class="actions">
        <button class="secondary" id="startCategoryQuiz">Questionnaire de préférences</button>
        <button class="secondary" id="startPracticeQuiz">Questionnaire de limites</button>
        <button class="secondary" id="startPositionQuiz">Questionnaire de postures</button>
      </div>
    `;
  }

  _renderQuiz() {
    const quiz = this._quiz;
    if (quiz.stepIndex < 0) return this._renderQuizPartnerPicker();
    if (quiz.kind === "practice") return this._renderPracticeQuizStep();
    if (quiz.kind === "position") return this._renderPositionQuizStep();
    return this._renderCategoryQuizStep();
  }

  _renderQuizPartnerPicker() {
    const cfg = this._config;
    return `
      <div class="draft">
        <h4>Qui répond à ce questionnaire ?</h4>
        <div class="note">Les réponses ne concernent que la personne qui répond. Passe l'appareil à cette personne, ou détourne le regard si vous êtes côte à côte.</div>
        <div class="actions">
          <button data-quiz-partner="${esc(cfg.partner1)}">${esc(cfg.partner1)}</button>
          <button data-quiz-partner="${esc(cfg.partner2)}">${esc(cfg.partner2)}</button>
        </div>
        <div class="actions">
          <button class="secondary" id="cancelQuiz">Annuler</button>
        </div>
      </div>
    `;
  }

  _renderCategoryQuizStep() {
    const quiz = this._quiz;
    const [key, label] = CATEGORIES[quiz.stepIndex] || [];
    if (!key) return "";

    return `
      <div class="draft">
        <h4>Préférences de ${esc(quiz.partner)} — ${quiz.stepIndex + 1}/${CATEGORIES.length}</h4>
        <div class="note">${esc(label)} : à quelle fréquence aimerais-tu que ce thème te soit proposé ?</div>
        <div class="chips">
          ${QUIZ_CHOICES.map(
            ([value, choiceLabel]) =>
              `<button class="chip quiz-choice" data-quiz-value="${value}">${esc(choiceLabel)}</button>`
          ).join("")}
        </div>
        <div class="actions">
          <button class="secondary" id="cancelQuiz">Annuler</button>
        </div>
      </div>
    `;
  }

  _renderPracticeQuizStep() {
    const quiz = this._quiz;
    const steps = flattenPracticeSteps();
    const step = steps[quiz.stepIndex];
    if (!step) return "";

    const cfg = this._config;
    const sexes = this._partnerSexes();
    const otherPartner = quiz.partner === cfg.partner1 ? cfg.partner2 : cfg.partner1;
    const questionText = step.text(sexes[quiz.partner], sexes[otherPartner]);

    return `
      <div class="draft">
        <h4>Limites de ${esc(quiz.partner)} — ${quiz.stepIndex + 1}/${steps.length}</h4>
        <div class="note"><strong>${esc(step.groupLabel)}</strong></div>
        <div class="note">${esc(questionText)}</div>
        <div class="chips">
          ${PRACTICE_ANSWER_CHOICES.map(
            ([value, choiceLabel]) =>
              `<button class="chip practice-choice" data-practice-value="${value}">${esc(choiceLabel)}</button>`
          ).join("")}
        </div>
        <div class="actions">
          <button class="secondary" id="cancelQuiz">Annuler</button>
        </div>
      </div>
    `;
  }

  _renderPositionQuizStep() {
    const quiz = this._quiz;
    const step = POSITION_QUESTIONS[quiz.stepIndex];
    if (!step) return "";
    const [, label, phrase] = step;

    return `
      <div class="draft">
        <h4>Postures de ${esc(quiz.partner)} — ${quiz.stepIndex + 1}/${POSITION_QUESTIONS.length}</h4>
        <div class="note"><strong>${esc(label)}</strong></div>
        <div class="note">Acceptes-tu de recevoir quelque chose (une caresse, une fessée...) ${esc(phrase)} ?</div>
        <div class="chips">
          ${PRACTICE_ANSWER_CHOICES.map(
            ([value, choiceLabel]) =>
              `<button class="chip position-choice" data-position-value="${value}">${esc(choiceLabel)}</button>`
          ).join("")}
        </div>
        <div class="actions">
          <button class="secondary" id="cancelQuiz">Annuler</button>
        </div>
      </div>
    `;
  }

  _renderPartnerBox(name, state, isMe) {
    if (!state) return "";
    const level = state.intensity || 0;
    const acc = state.accessories || [];
    const idea = state.new_idea_label;
    const lingerieLabels = state.lingerie_labels || [];
    const isFemme = this._partnerSexes()[name] === "Femme";
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
        ${acc.length ? `<div class="meta">\u{1F9FA} Accessoires : ${esc(acc.map(accessoryLabel).join(", "))}</div>` : ""}
        ${lingerieLabels.length ? `<div class="meta">\u{1F457} Tenue portée : ${esc(lingerieLabels.join(", "))}</div>` : ""}
        ${idea ? `<div class="meta">\u2728 ${esc(idea)}</div>` : ""}
        ${updated ? `<div class="meta">Mis à jour à ${updated}</div>` : ""}
        ${
          isMe && isFemme
            ? `<button class="chip lingerie-toggle ${lingerieLabels.length ? "on" : ""}" data-lingerie-partner="${esc(name)}">
                 ${lingerieLabels.length ? "\u{1F457} Modifier ma tenue" : "\u{1F457} J'ai enfilé une petite tenue"}
               </button>`
            : ""
        }
        ${
          isMe && isFemme && lingerieLabels.length
            ? `<button class="chip secondary" data-lingerie-clear="${esc(name)}">Je me suis changée</button>`
            : ""
        }
        ${
          isMe
            ? `<button class="chip brave-toggle ${state.brave_taboos ? "on" : ""}" data-brave-partner="${esc(name)}">
                 ${state.brave_taboos ? "\u{1F513} Interdits bravés" : "\u{1F512} Braver mes interdits"}
               </button>`
            : ""
        }
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
                       `<button class="chip ${draft.accessories.includes(a) ? "on" : ""}" data-accessory="${esc(a)}">${esc(accessoryLabel(a))}</button>`
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

  _renderLingerieDraft(data) {
    const draft = this._lingerieDraft;
    const lingerieOwned = data.accessories.filter((id) => {
      const item = ACCESSORY_CATALOG.find((i) => i.id === id);
      return item && item.category === "lingerie";
    });

    return `
      <div class="draft">
        <h4>\u{1F457} Tenue de ${esc(draft.partner)}</h4>
        ${
          lingerieOwned.length
            ? `<div class="note">Qu'as-tu enfilé ce soir ?</div>
               <div class="chips">
                 ${lingerieOwned
                   .map(
                     (id) =>
                       `<button class="chip ${draft.items.includes(id) ? "on" : ""}" data-lingerie-item="${esc(id)}">${esc(accessoryLabel(id))}</button>`
                   )
                   .join("")}
               </div>`
            : `<div class="note">Aucune lingerie enregistrée pour l'instant (voir « Préférences &amp; accessoires » plus bas).</div>`
        }
        <div class="actions">
          <button id="saveLingerie" ${draft.items.length ? "" : "disabled"}>Prévenir ${esc(data.other || "mon/ma partenaire")}</button>
          <button class="secondary" id="cancelLingerie">Annuler</button>
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

    if (data.bothEngaged) {
      return `
        <div class="section">
          <h3>Ce soir</h3>
          <div class="note">${esc(cfg.partner1)} et ${esc(cfg.partner2)} sont tous les deux prêts pour ce soir 🔥</div>
          <div class="actions">
            <button id="endEncounter">🎉 On a terminé de s'envoyer en l'air</button>
          </div>
        </div>
      `;
    }

    const draftOpen = this._draft && this._draft.open;
    const lingerieOpen = this._lingerieDraft && this._lingerieDraft.open;

    return `
      <div class="section">
        <h3>Ce soir</h3>
        ${this._renderPartnerBox(data.other, data.states[data.other], false)}
        ${this._renderPartnerBox(data.me, data.states[data.me], true)}
        ${
          lingerieOpen
            ? this._renderLingerieDraft(data)
            : draftOpen
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

    const endEncounterBtn = root.getElementById("endEncounter");
    if (endEncounterBtn) {
      endEncounterBtn.addEventListener("click", () => this._duoService("end_encounter", {}));
    }
    if (data.bothEngaged) return;

    root.querySelectorAll("[data-brave-partner]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const partner = btn.dataset.bravePartner;
        const current = (data.states[partner] || {}).brave_taboos;
        this._duoService("set_brave_taboos", { partner, enabled: !current });
      });
    });

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

    root.querySelectorAll("[data-lingerie-partner]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const partner = btn.dataset.lingeriePartner;
        const state = data.states[partner] || {};
        this._lingerieDraft = { open: true, partner, items: [...(state.lingerie || [])] };
        this._render();
      });
    });

    root.querySelectorAll("[data-lingerie-clear]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const partner = btn.dataset.lingerieClear;
        this._duoService("set_lingerie", { partner, items: [] });
      });
    });

    if (this._lingerieDraft && this._lingerieDraft.open) {
      root.querySelectorAll("[data-lingerie-item]").forEach((chip) => {
        chip.addEventListener("click", () => {
          const id = chip.dataset.lingerieItem;
          const list = this._lingerieDraft.items;
          const idx = list.indexOf(id);
          if (idx >= 0) list.splice(idx, 1);
          else list.push(id);
          chip.classList.toggle("on");
          const saveBtn = root.getElementById("saveLingerie");
          if (saveBtn) saveBtn.disabled = list.length === 0;
        });
      });

      const cancelLingerieBtn = root.getElementById("cancelLingerie");
      if (cancelLingerieBtn) {
        cancelLingerieBtn.addEventListener("click", () => {
          this._lingerieDraft = { open: false, partner: null, items: [] };
          this._render();
        });
      }

      const saveLingerieBtn = root.getElementById("saveLingerie");
      if (saveLingerieBtn) {
        saveLingerieBtn.addEventListener("click", () => {
          const draft = this._lingerieDraft;
          this._duoService("set_lingerie", { partner: draft.partner, items: draft.items });
          this._lingerieDraft = { open: false, partner: null, items: [] };
          this._render();
        });
      }
    }

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
    const themeKey = this._themeKey();
    const sessionPhase = this._eveningData().sessionPhase;
    const flame = themeKey === "amour" && sessionPhase === "phase_intense" ? "🔥 " : "";

    this._root.innerHTML = `
      <style>
        :host { display: block; }
        ${themeCss(themeKey, sessionPhase)}
        ha-card { padding: 16px; font-family: var(--paper-font-body1_-_font-family, inherit); }
        .title-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 12px; }
        .title { font-size: 1.2em; font-weight: 600; }
        .theme-picker { font-size: 0.75em; padding: 2px; border-radius: 6px; border: 1px solid var(--divider-color, #ccc); background: transparent; color: var(--primary-text-color, inherit); }
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
        .turn-hint {
          font-size: 0.9em; font-weight: 600; margin-bottom: 8px;
          color: var(--primary-color, #e91e63);
        }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .progress-outer {
          background: var(--divider-color, #ddd); border-radius: 6px; height: 10px; overflow: hidden; margin: 8px 0;
        }
        .progress-inner { background: var(--primary-color, #e91e63); height: 100%; }
        .reminder { font-size: 0.8em; opacity: 0.6; font-style: italic; margin-top: 6px; }
        .history-item { font-size: 0.85em; opacity: 0.8; padding: 2px 0; }
        details summary { cursor: pointer; opacity: 0.8; margin-bottom: 8px; }
        .pref-row { display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: 8px; margin-bottom: 4px; }
        .pref-value { min-width: 1.2em; text-align: center; font-weight: 600; opacity: 0.8; }
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
        .note { font-size: 0.85em; opacity: 0.7; margin-bottom: 8px; }
        .accessory-group { margin-bottom: 10px; }
        .accessory-group-title { font-size: 0.8em; font-weight: 600; opacity: 0.75; margin-bottom: 4px; }
      </style>
      <ha-card>
        <div class="title-row">
          <div class="title">${flame}💞 Duo — ${cfg.partner1} &amp; ${cfg.partner2}</div>
          <select class="theme-picker" id="themePicker" title="Thème de la carte">
            ${THEME_OPTIONS.map(
              ([k, l]) =>
                `<option value="${k}" ${k === themeKey ? "selected" : ""}>${esc(l)}</option>`
            ).join("")}
          </select>
        </div>

        ${this._renderTonight()}
        ${this._renderLevelProgress()}

        <div class="section">
          <h3>${flame}Suggestion</h3>
          ${
            suggestion && suggestion.attributes.description
              ? `
            <div class="suggestion-box">
              <div class="suggestion-name">${esc(suggestion.attributes.title || suggestion.state)}</div>
              <div class="suggestion-desc">${esc(suggestion.attributes.description)}</div>
              <div class="meta">
                Intensité : ${"♥".repeat(suggestion.attributes.intensity || 0)}${"♡".repeat(5 - (suggestion.attributes.intensity || 0))}
                ${
                  suggestion.attributes.duration_mode === "count"
                    ? ""
                    : ` · Durée : ${suggestion.attributes.duration_minutes} min`
                }
                ${
                  suggestion.attributes.position_label
                    ? ` · Position : ${esc(suggestion.attributes.position_label)}`
                    : ""
                }
                · Statut : ${esc(status)}
              </div>
              ${
                status === "proposed" && suggestion.attributes.turn
                  ? `<div class="turn-hint">👉 C'est à <strong>${esc(suggestion.attributes.turn)}</strong> de décider — passez-vous l'appareil si vous n'utilisez qu'un seul téléphone.</div>`
                  : ""
              }
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
          <div class="row">
            <label for="phasePicker">Phase visée</label>
            <select id="phasePicker">
              ${PHASES.map(
                ([k, l]) =>
                  `<option value="${k}" ${k === (this._selectedPhase || "") ? "selected" : ""}>${esc(l)}</option>`
              ).join("")}
            </select>
          </div>
          <div class="actions">
            <button id="request">Proposer une activité</button>
            <button class="secondary" id="reset">Réinitialiser</button>
          </div>
        </div>

        <div class="section">
          <h3>Minuteur</h3>
          <div>${fmtTime(remaining)} ${running ? "⏳" : ""}</div>
          <div class="progress-outer"><div class="progress-inner" style="width:${running ? progressPct : 0}%"></div></div>
          <div class="note">Bip toutes les 30 s, puis un bip différent chaque seconde dans les 10 dernières secondes.</div>
          <div class="actions">
            <button id="stopTimer" ${running ? "" : "disabled"}>Arrêter le minuteur</button>
            <button class="secondary" id="muteToggle">${this._isSoundMuted() ? "🔇 Son coupé" : "🔊 Son activé"}</button>
          </div>
        </div>

        <details class="section" id="prefsDetails" ${this._detailsOpen.prefs ? "open" : ""}>
          <summary>Préférences &amp; accessoires</summary>
          ${this._quiz.open ? this._renderQuiz() : this._renderQuizLauncher()}
          ${(() => {
            const data = this._eveningData();
            const renderSliders = (partnerNum, partnerName) => {
              const prefs = (data.states[partnerName] || {}).preferences || {};
              return `
              <h3>Préférences de ${esc(partnerName)}</h3>
              ${CATEGORIES.map(([k, l]) => {
                const rating = prefs[k] === undefined ? 3 : prefs[k];
                return `
                <div class="pref-row">
                  <label>${esc(l)}</label>
                  <input type="range" min="0" max="5" step="1" value="${rating}"
                    data-partner="${partnerNum}" data-category="${k}" class="pref-slider" />
                  <span class="pref-value">${rating}</span>
                </div>
              `;
              }).join("")}
            `;
            };
            // Identité connue (personne HA associée) : chacun ne voit et ne
            // modifie que ses propres curseurs. Sans association (appareil
            // partagé), on affiche les deux comme avant.
            if (data.me === cfg.partner1) return renderSliders(1, cfg.partner1);
            if (data.me === cfg.partner2) return renderSliders(2, cfg.partner2);
            return renderSliders(1, cfg.partner1) + renderSliders(2, cfg.partner2);
          })()}
          <h3>Accessoires possédés par le couple</h3>
          <div class="note">Cochez ce que vous possédez déjà. Modifiable aussi depuis la configuration de l'intégration Duo (Paramètres → Appareils et services → Duo → Configurer).</div>
          ${(() => {
            const owned = this._eveningData().accessories || [];
            return ACCESSORY_CATEGORIES.map(([catKey, catLabel]) => {
              const items = ACCESSORY_CATALOG.filter((item) => item.category === catKey);
              if (!items.length) return "";
              return `
                <div class="accessory-group">
                  <div class="accessory-group-title">${esc(catLabel)}</div>
                  <div class="chips">
                    ${items
                      .map(
                        (item) => `
                      <button class="chip accessory-chip ${owned.includes(item.id) ? "on" : ""}"
                        data-accessory-id="${esc(item.id)}">${esc(item.label)}${esc(accessorySexHint(item))}</button>
                    `
                      )
                      .join("")}
                  </div>
                </div>
              `;
            }).join("");
          })()}
        </details>

        ${
          history && history.attributes.last_entries && history.attributes.last_entries.length
            ? `
          <details class="section" id="historyDetails" ${this._detailsOpen.history ? "open" : ""}>
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

    const themePicker = root.getElementById("themePicker");
    if (themePicker) {
      themePicker.addEventListener("change", () => this._setThemeKey(themePicker.value));
    }

    const prefsDetails = root.getElementById("prefsDetails");
    if (prefsDetails) {
      prefsDetails.addEventListener("toggle", () => {
        this._detailsOpen.prefs = prefsDetails.open;
      });
    }

    const closedQuiz = () => ({ open: false, kind: null, stepIndex: -1, partner: null, answers: {} });

    const startQuiz = (kind) => {
      const data = this._eveningData();
      const partner = data.me || null;
      this._quiz = { open: true, kind, stepIndex: partner ? 0 : -1, partner, answers: {} };
      this._detailsOpen.prefs = true;
      this._render();
    };

    const startCategoryQuizBtn = root.getElementById("startCategoryQuiz");
    if (startCategoryQuizBtn) {
      startCategoryQuizBtn.addEventListener("click", () => startQuiz("category"));
    }
    const startPracticeQuizBtn = root.getElementById("startPracticeQuiz");
    if (startPracticeQuizBtn) {
      startPracticeQuizBtn.addEventListener("click", () => startQuiz("practice"));
    }
    const startPositionQuizBtn = root.getElementById("startPositionQuiz");
    if (startPositionQuizBtn) {
      startPositionQuizBtn.addEventListener("click", () => startQuiz("position"));
    }

    const cancelQuizBtn = root.getElementById("cancelQuiz");
    if (cancelQuizBtn) {
      cancelQuizBtn.addEventListener("click", () => {
        this._quiz = closedQuiz();
        this._render();
      });
    }

    root.querySelectorAll("[data-quiz-partner]").forEach((btn) => {
      btn.addEventListener("click", () => {
        this._quiz.partner = btn.dataset.quizPartner;
        this._quiz.stepIndex = 0;
        this._render();
      });
    });

    root.querySelectorAll(".quiz-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        const quiz = this._quiz;
        const [key] = CATEGORIES[quiz.stepIndex] || [];
        if (!key) return;
        quiz.answers[key] = Number(btn.dataset.quizValue);
        quiz.stepIndex += 1;
        if (quiz.stepIndex >= CATEGORIES.length) {
          const partner = quiz.partner;
          Object.entries(quiz.answers).forEach(([category, rating]) => {
            this._duoService("set_preference", { partner, category, rating });
          });
          this._quiz = closedQuiz();
        }
        this._render();
      });
    });

    root.querySelectorAll(".practice-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        const quiz = this._quiz;
        const steps = flattenPracticeSteps();
        const step = steps[quiz.stepIndex];
        if (!step) return;
        quiz.answers[`${step.groupKey}_${step.role}`] = btn.dataset.practiceValue;
        quiz.stepIndex += 1;
        if (quiz.stepIndex >= steps.length) {
          const partner = quiz.partner;
          Object.entries(quiz.answers).forEach(([key, answer]) => {
            this._duoService("set_practice_limit", { partner, key, answer });
          });
          this._quiz = closedQuiz();
        }
        this._render();
      });
    });

    root.querySelectorAll(".position-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        const quiz = this._quiz;
        const step = POSITION_QUESTIONS[quiz.stepIndex];
        if (!step) return;
        const [position] = step;
        quiz.answers[position] = btn.dataset.positionValue;
        quiz.stepIndex += 1;
        if (quiz.stepIndex >= POSITION_QUESTIONS.length) {
          const partner = quiz.partner;
          Object.entries(quiz.answers).forEach(([position, answer]) => {
            this._duoService("set_position_limit", { partner, position, answer });
          });
          this._quiz = closedQuiz();
        }
        this._render();
      });
    });
    const historyDetails = root.getElementById("historyDetails");
    if (historyDetails) {
      historyDetails.addEventListener("toggle", () => {
        this._detailsOpen.history = historyDetails.open;
      });
    }

    this._attachTonightEvents();

    const phasePicker = root.getElementById("phasePicker");
    if (phasePicker) {
      phasePicker.addEventListener("change", () => {
        this._selectedPhase = phasePicker.value;
      });
    }

    const prevPhaseBtn = root.getElementById("prevPhase");
    if (prevPhaseBtn && !prevPhaseBtn.disabled) {
      prevPhaseBtn.addEventListener("click", () =>
        this._duoService("set_phase", { phase: prevPhaseBtn.dataset.phase })
      );
    }
    const nextPhaseBtn = root.getElementById("nextPhase");
    if (nextPhaseBtn && !nextPhaseBtn.disabled) {
      nextPhaseBtn.addEventListener("click", () =>
        this._duoService("set_phase", { phase: nextPhaseBtn.dataset.phase })
      );
    }

    const requestBtn = root.getElementById("request");
    if (requestBtn)
      requestBtn.addEventListener("click", () =>
        this._duoService("request_suggestion", {
          ...(this._selectedPhase ? { phase: this._selectedPhase } : {}),
        })
      );

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

    const muteToggleBtn = root.getElementById("muteToggle");
    if (muteToggleBtn) {
      muteToggleBtn.addEventListener("click", () => this._setSoundMuted(!this._isSoundMuted()));
    }

    root.querySelectorAll(".accessory-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const owned = new Set(this._eveningData().accessories || []);
        const id = chip.dataset.accessoryId;
        if (owned.has(id)) owned.delete(id);
        else owned.add(id);
        this._duoService("set_accessories", { accessories: Array.from(owned) });
      });
    });

    root.querySelectorAll(".pref-slider").forEach((slider) => {
      const valueLabel = slider.nextElementSibling;
      slider.addEventListener("input", () => {
        if (valueLabel && valueLabel.classList.contains("pref-value")) {
          valueLabel.textContent = slider.value;
        }
      });
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
  evening_entity: "Entité soirée",
  history_entity: "Entité historique (facultatif)",
  mood_entity_partner1: "Humeur du partenaire 1 (facultatif)",
  mood_entity_partner2: "Humeur du partenaire 2 (facultatif)",
  theme: "Thème par défaut de la carte (facultatif)",
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
      { name: "evening_entity", required: true, selector: sensor },
      { name: "history_entity", selector: sensor },
      { name: "mood_entity_partner1", selector: select },
      { name: "mood_entity_partner2", selector: select },
      {
        name: "theme",
        selector: {
          select: {
            options: THEME_OPTIONS.map(([value, label]) => ({ value, label })),
            mode: "dropdown",
          },
        },
      },
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
