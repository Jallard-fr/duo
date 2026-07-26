"""Constants for the Duo integration."""

DOMAIN = "duo"
STORAGE_VERSION = 1

CONF_PARTNER1 = "partner1"
CONF_PARTNER2 = "partner2"
CONF_CONSENT = "consent"

CATEGORY_PRELIMINAIRES = "preliminaires"
CATEGORY_SENSORIEL = "sensoriel"
CATEGORY_MASSAGE = "massage"
CATEGORY_JEU_DE_ROLE = "jeu_de_role"
CATEGORY_COMMUNICATION = "communication"
CATEGORY_INTENSITE_PLUS = "intensite_plus"

CATEGORIES = [
    CATEGORY_PRELIMINAIRES,
    CATEGORY_SENSORIEL,
    CATEGORY_MASSAGE,
    CATEGORY_JEU_DE_ROLE,
    CATEGORY_COMMUNICATION,
    CATEGORY_INTENSITE_PLUS,
]

CATEGORY_LABELS = {
    CATEGORY_PRELIMINAIRES: "Préliminaires",
    CATEGORY_SENSORIEL: "Sensoriel",
    CATEGORY_MASSAGE: "Massage",
    CATEGORY_JEU_DE_ROLE: "Jeu de rôle",
    CATEGORY_COMMUNICATION: "Communication & Fantasmes",
    CATEGORY_INTENSITE_PLUS: "Intensité +",
}

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

SIGNAL_UPDATE = "duo_update_{entry_id}"

# How long (in days) a declined activity stays "on hold" before it can be
# proposed again automatically. It can still resurface earlier if the
# partner concerned explicitly picks the "novelty" mood.
DECLINE_COOLDOWN_DAYS = 14

DEFAULT_PROFILE = {
    "preferences": {},  # {partner: {category: rating(0-5)}}
    "accessories": [],  # list[str]
    "moods": {},  # {partner: mood}
    "declined": {},  # {activity_id: iso_timestamp}
    "history": [],  # list of {activity_id, response, timestamp, turn}
}
