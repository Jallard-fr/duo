"""Constants for the Duo integration."""

DOMAIN = "duo"
STORAGE_VERSION = 1

CONF_PARTNER1 = "partner1"
CONF_PARTNER2 = "partner2"
CONF_PARTNER1_SEX = "partner1_sex"
CONF_PARTNER2_SEX = "partner2_sex"
CONF_CONSENT = "consent"

SEX_HOMME = "homme"
SEX_FEMME = "femme"
SEX_INDIFFERENT = "indifferent"

# Un partenaire est "homme" ou "femme". Les activités acceptent en plus
# "indifferent" pour leurs champs actor_sex/receiver_sex, ce qui signifie
# que l'activité s'applique quel que soit le sexe de ce partenaire.
PARTNER_SEX_OPTIONS = [SEX_HOMME, SEX_FEMME]
ACTIVITY_SEX_OPTIONS = [SEX_HOMME, SEX_FEMME, SEX_INDIFFERENT]

SEX_LABELS = {
    SEX_HOMME: "Homme",
    SEX_FEMME: "Femme",
    SEX_INDIFFERENT: "Indifférent",
}

# Association partenaire de jeu <-> personne Home Assistant (entités person.*)
CONF_PERSON1 = "person1"
CONF_PERSON2 = "person2"
# Surcharge manuelle des cibles de notification (services notify.*, séparés
# par des virgules). Laisser vide pour une détection automatique via les
# appareils mobile_app rattachés à l'utilisateur.
CONF_NOTIFY1 = "notify1"
CONF_NOTIFY2 = "notify2"
# Champ du formulaire d'options utilisé pour cocher, parmi le catalogue
# prédéfini (voir accessories.py), les accessoires possédés par le couple.
# Volontairement pas stocké dans entry.options : la liste réelle reste dans
# le profil persistant (Store), comme lorsqu'elle est modifiée via le
# service duo.set_accessories ou depuis la carte.
CONF_ACCESSORIES = "accessories"

CATEGORY_PRELIMINAIRES = "preliminaires"
CATEGORY_SENSORIEL = "sensoriel"
CATEGORY_MASSAGE = "massage"
CATEGORY_JEU_DE_ROLE = "jeu_de_role"
CATEGORY_COMMUNICATION = "communication"
CATEGORY_INTENSITE_PLUS = "intensite_plus"
CATEGORY_RESOLUTION = "resolution"

CATEGORIES = [
    CATEGORY_PRELIMINAIRES,
    CATEGORY_SENSORIEL,
    CATEGORY_MASSAGE,
    CATEGORY_JEU_DE_ROLE,
    CATEGORY_COMMUNICATION,
    CATEGORY_INTENSITE_PLUS,
    CATEGORY_RESOLUTION,
]

CATEGORY_LABELS = {
    CATEGORY_PRELIMINAIRES: "Préliminaires",
    CATEGORY_SENSORIEL: "Sensoriel",
    CATEGORY_MASSAGE: "Massage",
    CATEGORY_JEU_DE_ROLE: "Jeu de rôle",
    CATEGORY_COMMUNICATION: "Communication & Fantasmes",
    CATEGORY_INTENSITE_PLUS: "Intensité +",
    CATEGORY_RESOLUTION: "Tendresse & après",
}

# ---------------------------------------------------------------------------
# Phases temporelles d'un rapport, des préliminaires à l'après.
#
# Inspiré du modèle des phases de la réponse sexuelle de Masters & Johnson
# (1966) et du modèle triphasique de Kaplan (1979) — les références les
# plus citées en sexologie pour découper un rapport dans le temps — puis
# adapté à un usage pratique et concret pour le couple :
#   1. Excitation    : encore habillés, début de la stimulation (ex. un
#                       partenaire va mettre une tenue sexy).
#   2. Préliminaires  : contacts avec les zones érogènes (baisers, caresses
#                       des doigts ou de la bouche — une pénétration
#                       digitale relève encore de cette phase).
#   3. Intense        : actions avec pénétration intense (ex. usage d'un
#                       accessoire vibrant à deux).
#   4. Résolution      : retour au calme, tendresse après le rapport.
# Une suggestion peut être demandée pour une phase précise afin
# d'accompagner la progression du moment, plutôt que de proposer
# n'importe quoi à n'importe quel instant.
# ---------------------------------------------------------------------------
PHASE_EXCITATION = "phase_excitation"
PHASE_PRELIMINAIRES = "phase_preliminaires"
PHASE_INTENSE = "phase_intense"
PHASE_RESOLUTION = "phase_resolution"

PHASES = [
    PHASE_EXCITATION,
    PHASE_PRELIMINAIRES,
    PHASE_INTENSE,
    PHASE_RESOLUTION,
]

PHASE_LABELS = {
    PHASE_EXCITATION: "Excitation",
    PHASE_PRELIMINAIRES: "Préliminaires",
    PHASE_INTENSE: "Intense",
    PHASE_RESOLUTION: "Résolution",
}

PHASE_DESCRIPTIONS = {
    PHASE_EXCITATION: "Encore habillés, on commence à se stimuler (ex. une tenue sexy).",
    PHASE_PRELIMINAIRES: "Contacts avec les zones érogènes : baisers, caresses des doigts ou de la bouche.",
    PHASE_INTENSE: "Actions avec pénétration intense.",
    PHASE_RESOLUTION: "Retour au calme, tendresse et proximité après le rapport.",
}

# ---------------------------------------------------------------------------
# Limites par pratique : contrairement aux catégories (larges, ex.
# "intensite_plus"), ces réponses ciblent des pratiques précises, sur le
# modèle d'une liste de consentement "oui / à voir / non" utilisée en
# thérapie de couple. "donne"/"recoit" distingue le rôle actif du rôle
# passif ; "usage" (jouets) est symétrique. Une réponse "non" exclut
# l'activité correspondante (voir practice_* dans activities.py), sauf si
# le partenaire concerné a activé "braver ses interdits".
# ---------------------------------------------------------------------------
PRACTICE_ANSWER_OUI = "oui"
PRACTICE_ANSWER_A_VOIR = "a_voir"
PRACTICE_ANSWER_NON = "non"

PRACTICE_ANSWERS = [PRACTICE_ANSWER_OUI, PRACTICE_ANSWER_A_VOIR, PRACTICE_ANSWER_NON]

PRACTICE_ANSWER_LABELS = {
    PRACTICE_ANSWER_OUI: "Oui",
    PRACTICE_ANSWER_A_VOIR: "À voir",
    PRACTICE_ANSWER_NON: "Non",
}

PRACTICE_ORAL = "oral"
PRACTICE_ANAL = "anal"
PRACTICE_DISCIPLINE = "discipline"
PRACTICE_LIENS = "liens"
PRACTICE_JOUETS = "jouets"

PRACTICES = [PRACTICE_ORAL, PRACTICE_ANAL, PRACTICE_DISCIPLINE, PRACTICE_LIENS, PRACTICE_JOUETS]

PRACTICE_LABELS = {
    PRACTICE_ORAL: "Stimulation orale",
    PRACTICE_ANAL: "Pénétration anale",
    PRACTICE_DISCIPLINE: "Discipline légère (fessée, fouet léger)",
    PRACTICE_LIENS: "Contrainte douce / liens",
    PRACTICE_JOUETS: "Jouets vibrants",
}

# ---------------------------------------------------------------------------
# Positions génériques, proposées comme simple élément de mise en scène pour
# une activité (jamais associées à une description d'acte explicite).
# ---------------------------------------------------------------------------
POSITION_ALLONGE = "position_allonge"
POSITION_QUATRE_PATTES = "position_quatre_pattes"
POSITION_PENCHE_AVANT = "position_penche_avant"
POSITION_DEBOUT = "position_debout"
POSITION_ASSIS = "position_assis"
POSITION_GENOUX = "position_genoux"

POSITIONS = [
    POSITION_ALLONGE,
    POSITION_QUATRE_PATTES,
    POSITION_PENCHE_AVANT,
    POSITION_DEBOUT,
    POSITION_ASSIS,
    POSITION_GENOUX,
]

POSITION_LABELS = {
    POSITION_ALLONGE: "Allongé(e)",
    POSITION_QUATRE_PATTES: "À quatre pattes",
    POSITION_PENCHE_AVANT: "Penché(e) en avant",
    POSITION_DEBOUT: "Debout",
    POSITION_ASSIS: "Assis(e)",
    POSITION_GENOUX: "À genoux",
}

# ---------------------------------------------------------------------------
# Progression guidée par niveau (= phase) : santé et plaisir avant tout, donc
# des activités volontairement courtes (3 minutes maximum, ou quantifiées en
# nombre d'actions plutôt qu'en temps) plutôt qu'une seule longue séquence.
# Chaque partenaire doit accepter un nombre donné d'activités de la phase en
# cours avant qu'elle ne passe automatiquement à la suivante (voir
# PHASE_TARGET_COUNTS ; LEVEL_TARGET_COUNT reste la valeur par défaut pour
# les phases non listées). En cas de refus, une nouvelle proposition est
# faite automatiquement, jusqu'à MAX_REROLLS fois avant de laisser la main
# au couple.
#
# La phase Préliminaires compte volontairement plus de tours (5, contre 3
# ailleurs) car trois règles de progression s'y appliquent, par acteur :
# - la pénétration (doigtage, jouet...) n'est proposée qu'aux 2 derniers
#   tours (4 et 5), et est garantie sur au moins l'un des deux ;
# - le sexe oral n'est proposé qu'à partir du 3e tour ;
# - l'intensité proposée suit elle aussi l'avancement du tour (voir
#   PRELIMINAIRES_INTENSITY_RANGE) : une fenêtre de 3 cœurs qui glisse d'au
#   plus un cœur par tour, pour une montée en intensité progressive plutôt
#   que de piocher n'importe quelle intensité dès le début.
# Voir DuoCoordinator._matches_preliminaires_turn et
# DuoCoordinator._preliminaires_penetration_done.
# ---------------------------------------------------------------------------
MAX_ACTIVITY_MINUTES = 3
LEVEL_TARGET_COUNT = 3
MAX_REROLLS = 4

PRELIMINAIRES_TARGET_COUNT = 5
PHASE_TARGET_COUNTS = {
    PHASE_PRELIMINAIRES: PRELIMINAIRES_TARGET_COUNT,
}

# {tour: (intensité min, intensité max)}, en cœurs (1 à 5).
PRELIMINAIRES_INTENSITY_RANGE = {
    1: (1, 2),
    2: (1, 3),
    3: (2, 4),
    4: (3, 5),
    5: (3, 5),
}

# Bornes du tirage aléatoire pour toute activité quantifiée en nombre
# d'actions ("count") plutôt qu'en temps : le nombre affiché est retiré à
# chaque nouvelle proposition, entre ces deux bornes, plutôt que fixé une
# fois pour toutes dans le catalogue (voir DuoCoordinator.current_count).
COUNT_MIN = 5
COUNT_MAX = 15

MOOD_NOT_TONIGHT = "pas_ce_soir"
MOOD_TENDERNESS = "douceur"
MOOD_CURIOUS = "curieux"
MOOD_NOVELTY = "nouveaute"
MOOD_TORRID = "torride"

MOOD_OPTIONS = [
    MOOD_NOT_TONIGHT,
    MOOD_TENDERNESS,
    MOOD_CURIOUS,
    MOOD_NOVELTY,
    MOOD_TORRID,
]

MOOD_LABELS = {
    MOOD_NOT_TONIGHT: "Pas ce soir",
    MOOD_TENDERNESS: "Envie de douceur",
    MOOD_CURIOUS: "Curieux(se)",
    MOOD_NOVELTY: "Envie de nouveauté",
    MOOD_TORRID: "Envie de torride",
}

# Intensité de l'envie, de 0 (aucune) à 4 (maximale).
MOOD_INTENSITY = {
    MOOD_NOT_TONIGHT: 0,
    MOOD_TENDERNESS: 1,
    MOOD_CURIOUS: 2,
    MOOD_NOVELTY: 3,
    MOOD_TORRID: 4,
}

MOOD_EMOJI = {
    MOOD_NOT_TONIGHT: "😴",
    MOOD_TENDERNESS: "💗",
    MOOD_CURIOUS: "😏",
    MOOD_NOVELTY: "✨",
    MOOD_TORRID: "🔥",
}

MOOD_MAX_INTENSITY = 4


def mood_gauge(mood: str) -> str:
    """Jauge visuelle de l'envie, ex. ❤️❤️🤍🤍."""
    level = MOOD_INTENSITY.get(mood, 0)
    return "❤️" * level + "🤍" * (MOOD_MAX_INTENSITY - level)


# Valeur spéciale renvoyée quand le partenaire ne sait pas encore ce qu'il
# aurait envie d'essayer de nouveau.
NEW_IDEA_UNKNOWN = "__unknown__"
NEW_IDEA_UNKNOWN_LABEL = "Rien de précis, à découvrir ensemble"

STATUS_IDLE = "idle"
STATUS_PROPOSED = "proposed"
STATUS_ACCEPTED = "accepted"
STATUS_DECLINED = "declined"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"

SERVICE_SET_PREFERENCE = "set_preference"
SERVICE_SET_ACCESSORIES = "set_accessories"
SERVICE_SET_MOOD = "set_mood"
SERVICE_REQUEST_SUGGESTION = "request_suggestion"
SERVICE_RESPOND_SUGGESTION = "respond_suggestion"
SERVICE_START_TIMER = "start_timer"
SERVICE_STOP_TIMER = "stop_timer"
SERVICE_RESET_SESSION = "reset_session"
SERVICE_CLEAR_PROFILE = "clear_profile"
SERVICE_SET_BRAVE_TABOOS = "set_brave_taboos"
SERVICE_SET_PRACTICE_LIMIT = "set_practice_limit"
SERVICE_SET_LINGERIE = "set_lingerie"
SERVICE_SET_POSITION_LIMIT = "set_position_limit"
SERVICE_SET_PHASE = "set_phase"
SERVICE_END_ENCOUNTER = "end_encounter"

SIGNAL_UPDATE = "duo_update_{entry_id}"

# How long (in days) a declined activity stays "on hold" before it can be
# proposed again automatically. It can still resurface earlier if the
# partner concerned explicitly picks the "novelty" mood.
DECLINE_COOLDOWN_DAYS = 14

DEFAULT_PROFILE = {
    "preferences": {},  # {partner: {category: rating(0-5)}} — 0 = jamais proposé
    "accessories": [],  # list[str]
    "moods": {},  # {partner: mood}
    "declined": {},  # {activity_id: iso_timestamp}
    "history": [],  # list of {activity_id, response, timestamp, turn}
    # Un partenaire qui active "braver ses interdits" redevient éligible aux
    # catégories qu'il a mises à 0 et aux activités en cooldown, jusqu'à ce
    # qu'il désactive à nouveau ce mode.
    "brave_taboos": {},  # {partner: bool}
    "practice_limits": {},  # {partner: {"oral_donne": "oui"|"a_voir"|"non", ...}}
    # Limites par posture (voir POSITION_* ci-dessus) : la question porte
    # toujours sur la posture dans laquelle ce partenaire REÇOIT quelque
    # chose (une caresse, une fessée...), jamais sur celle de l'autre.
    "position_limits": {},  # {partner: {"position_allonge": "oui"|"a_voir"|"non", ...}}
    # État de la soirée en cours, remis à zéro chaque nuit à minuit.
    # {partner: {"accessories": [...], "new_idea": str|None, "lingerie": [...],
    #            "engaged": bool, "updated": iso}}
    "evening": {},
}
