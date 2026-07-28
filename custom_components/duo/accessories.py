"""Predefined accessory catalog for the Duo integration.

Rather than typing free-text accessory names, partners simply check which
items from this catalog they already own ("leur stock"). Categories and
entries are the generic, commonly used names found on mainstream online
retailers for couples' intimate wellness products — no explicit or
graphic content, just category labels used to filter suggestions.

Just like activities, each accessory carries an ``actor_sex`` and a
``receiver_sex`` field (``homme``, ``femme`` or ``indifferent``). Here the
"actor" is the partner who wears/uses the accessory, the "receiver" is the
other partner. For example, item-specific lingerie is worn by an actor of
a given sex regardless of the receiver's sex, while a couple's vibrator
designed for female anatomy is only relevant when the receiver is a
woman, regardless of who puts it in place. Both fields default to
"indifferent" for accessories that aren't tied to anatomy or a typical
wearer (bandages, dice, restraints, massage oil...).
"""

from .const import SEX_FEMME, SEX_HOMME, SEX_INDIFFERENT

ACCESSORY_CATEGORY_SENSORIEL = "sensoriel"
ACCESSORY_CATEGORY_JEUX = "jeux"
ACCESSORY_CATEGORY_VIBRANT = "vibrant"
ACCESSORY_CATEGORY_CONTRAINTE_DOUCE = "contrainte_douce"
ACCESSORY_CATEGORY_LINGERIE = "lingerie"
ACCESSORY_CATEGORY_SOINS = "soins"

ACCESSORY_CATEGORIES = [
    (ACCESSORY_CATEGORY_SENSORIEL, "Sensoriel & bien-être"),
    (ACCESSORY_CATEGORY_JEUX, "Jeux de couple"),
    (ACCESSORY_CATEGORY_VIBRANT, "Accessoires vibrants"),
    (ACCESSORY_CATEGORY_CONTRAINTE_DOUCE, "Contrainte douce"),
    (ACCESSORY_CATEGORY_LINGERIE, "Lingerie & tenues"),
    (ACCESSORY_CATEGORY_SOINS, "Soins & confort"),
]


def _item(item_id: str, label: str, category: str, *, actor_sex: str = SEX_INDIFFERENT, receiver_sex: str = SEX_INDIFFERENT) -> dict:
    return {
        "id": item_id,
        "label": label,
        "category": category,
        "actor_sex": actor_sex,
        "receiver_sex": receiver_sex,
    }


# Les identifiants "bandeau", "glaçons", "plume" et "huile de massage"
# correspondent aux accessoires déjà référencés dans activities.py : ne pas
# les renommer sans mettre à jour ce fichier en conséquence.
ACCESSORY_CATALOG = [
    _item("bandeau", "Bandeau / masque", ACCESSORY_CATEGORY_SENSORIEL),
    _item("plume", "Plumes", ACCESSORY_CATEGORY_SENSORIEL),
    _item("glaçons", "Glaçons", ACCESSORY_CATEGORY_SENSORIEL),
    _item("huile de massage", "Huile de massage", ACCESSORY_CATEGORY_SENSORIEL),
    _item("bougie de massage", "Bougie de massage basse température", ACCESSORY_CATEGORY_SENSORIEL),
    _item("foulards", "Foulards / liens doux", ACCESSORY_CATEGORY_SENSORIEL),

    _item("des_du_desir", "Dés du désir", ACCESSORY_CATEGORY_JEUX),
    _item("cartes_jeu_couple", "Cartes de jeu pour couple", ACCESSORY_CATEGORY_JEUX),
    _item("kit_jeu_de_role", "Kit de jeu de rôle / déguisement léger", ACCESSORY_CATEGORY_JEUX),
    _item("jeu_societe_coquin", "Jeu de société coquin", ACCESSORY_CATEGORY_JEUX),

    # Jouets vibrants conçus pour une stimulation typiquement féminine
    # (clitoridienne / point G) : pertinents quel que soit qui les manie,
    # mais seulement quand la personne qui reçoit est une femme.
    _item("vibromasseur", "Vibromasseur", ACCESSORY_CATEGORY_VIBRANT, receiver_sex=SEX_FEMME),
    _item("rabbit_double", "Rabbit double", ACCESSORY_CATEGORY_VIBRANT, receiver_sex=SEX_FEMME),
    _item("satisfyer", "Satisfyer", ACCESSORY_CATEGORY_VIBRANT, receiver_sex=SEX_FEMME),
    _item("mini_vibro", "Mini-vibro discret", ACCESSORY_CATEGORY_VIBRANT, receiver_sex=SEX_FEMME),
    _item("masseur_couple", "Masseur pour couple", ACCESSORY_CATEGORY_VIBRANT, receiver_sex=SEX_FEMME),
    # Anneau vibrant : porté par l'acteur homme, bénéficie aux deux partenaires.
    _item("bague_vibrante", "Bague vibrante", ACCESSORY_CATEGORY_VIBRANT, actor_sex=SEX_HOMME),

    # La contrainte douce n'est pas liée au sexe des partenaires : les deux
    # rôles (qui attache / qui est attaché) restent indifférents.
    _item("menottes_douces", "Menottes douces", ACCESSORY_CATEGORY_CONTRAINTE_DOUCE),
    _item("corde_bondage_debutant", "Corde de bondage débutant", ACCESSORY_CATEGORY_CONTRAINTE_DOUCE),
    _item("fouet_leger", "Fouet léger / palette", ACCESSORY_CATEGORY_CONTRAINTE_DOUCE),

    # Lingerie fine : portée par l'acteur femme, peu importe le récepteur.
    _item("lingerie_fine", "Lingerie fine", ACCESSORY_CATEGORY_LINGERIE, actor_sex=SEX_FEMME),
    # Déguisement et masque sexy : portés par l'acteur femme, peu importe
    # le récepteur (même logique que la lingerie fine ci-dessus).
    _item("tenue_legere", "Déguisement sexy femme", ACCESSORY_CATEGORY_LINGERIE, actor_sex=SEX_FEMME),
    _item("masque", "Masque sexy femme", ACCESSORY_CATEGORY_LINGERIE, actor_sex=SEX_FEMME),

    _item("lubrifiant", "Lubrifiant", ACCESSORY_CATEGORY_SOINS),
    _item("gel_chauffant", "Gel chauffant / rafraîchissant", ACCESSORY_CATEGORY_SOINS),
    # Préservatif externe : porté par l'acteur homme, peu importe le récepteur.
    _item("preservatifs", "Préservatifs", ACCESSORY_CATEGORY_SOINS, actor_sex=SEX_HOMME),
]

ACCESSORY_LABELS = {item["id"]: item["label"] for item in ACCESSORY_CATALOG}
ACCESSORY_BY_ID = {item["id"]: item for item in ACCESSORY_CATALOG}
ACCESSORY_CATEGORY_LABELS = dict(ACCESSORY_CATEGORIES)


def accessory_matches_sex(accessory_id: str, actor_sex: str, receiver_sex: str) -> bool:
    """Whether an accessory applies to the given actor/receiver sex pairing.

    Unknown accessory ids (e.g. a couple's own free-form entry from before
    this catalog existed) are treated as always applicable.
    """
    item = ACCESSORY_BY_ID.get(accessory_id)
    if item is None:
        return True
    item_actor_sex = item.get("actor_sex", SEX_INDIFFERENT)
    item_receiver_sex = item.get("receiver_sex", SEX_INDIFFERENT)
    actor_ok = item_actor_sex in (SEX_INDIFFERENT, actor_sex)
    receiver_ok = item_receiver_sex in (SEX_INDIFFERENT, receiver_sex)
    return actor_ok and receiver_ok


def owned_item_in_category(owned_ids: list[str], category: str, actor_sex: str, receiver_sex: str) -> str | None:
    """First owned accessory id in `category` that also matches the given
    actor/receiver sex, if any. Lets an activity reference a whole family of
    interchangeable accessories (e.g. "un jouet vibrant", quel qu'il soit)
    instead of a single specific product id."""
    for accessory_id in owned_ids:
        item = ACCESSORY_BY_ID.get(accessory_id)
        if item and item["category"] == category and accessory_matches_sex(accessory_id, actor_sex, receiver_sex):
            return accessory_id
    return None


def accessories_by_category() -> dict[str, list[dict]]:
    """Group the catalog by category, preserving ACCESSORY_CATEGORIES order."""
    grouped: dict[str, list[dict]] = {key: [] for key, _ in ACCESSORY_CATEGORIES}
    for item in ACCESSORY_CATALOG:
        grouped.setdefault(item["category"], []).append(item)
    return grouped


def accessory_categories_as_list() -> list[dict]:
    """JSON-friendly form of ACCESSORY_CATEGORIES, for exposing it as an
    entity attribute that the frontend card reads instead of keeping its
    own copy of the catalog."""
    return [{"key": key, "label": label} for key, label in ACCESSORY_CATEGORIES]
