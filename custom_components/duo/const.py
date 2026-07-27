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
    # État de la soirée en cours, remis à zéro chaque nuit à minuit.
    # {partner: {"accessories": [...], "new_idea": str|None, "updated": iso}}
    "evening": {},
}
