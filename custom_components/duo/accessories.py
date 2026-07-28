"""Predefined accessory catalog for the Duo integration.

Rather than typing free-text accessory names, partners simply check which
items from this catalog they already own ("leur stock"). Categories and
entries are the generic, commonly used names found on mainstream online
retailers for couples' intimate wellness products — no explicit or
graphic content, just category labels used to filter suggestions.
"""

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

# Les identifiants "bandeau", "glaçons", "plume" et "huile de massage"
# correspondent aux accessoires déjà référencés dans activities.py : ne pas
# les renommer sans mettre à jour ce fichier en conséquence.
ACCESSORY_CATALOG = [
    {"id": "bandeau", "label": "Bandeau / masque", "category": ACCESSORY_CATEGORY_SENSORIEL},
    {"id": "plume", "label": "Plumes", "category": ACCESSORY_CATEGORY_SENSORIEL},
    {"id": "glaçons", "label": "Glaçons", "category": ACCESSORY_CATEGORY_SENSORIEL},
    {"id": "huile de massage", "label": "Huile de massage", "category": ACCESSORY_CATEGORY_SENSORIEL},
    {"id": "bougie de massage", "label": "Bougie de massage basse température", "category": ACCESSORY_CATEGORY_SENSORIEL},
    {"id": "foulards", "label": "Foulards / liens doux", "category": ACCESSORY_CATEGORY_SENSORIEL},

    {"id": "des_du_desir", "label": "Dés du désir", "category": ACCESSORY_CATEGORY_JEUX},
    {"id": "cartes_jeu_couple", "label": "Cartes de jeu pour couple", "category": ACCESSORY_CATEGORY_JEUX},
    {"id": "kit_jeu_de_role", "label": "Kit de jeu de rôle / déguisement léger", "category": ACCESSORY_CATEGORY_JEUX},
    {"id": "jeu_societe_coquin", "label": "Jeu de société coquin", "category": ACCESSORY_CATEGORY_JEUX},

    {"id": "vibromasseur", "label": "Vibromasseur", "category": ACCESSORY_CATEGORY_VIBRANT},
    {"id": "RabbitD", "label": "Rabbit double", "category": ACCESSORY_CATEGORY_VIBRANT},
    {"id": "Satisfyer", "label": "Satisfyer", "category": ACCESSORY_CATEGORY_VIBRANT},
    {"id": "bague_vibrante", "label": "Bague vibrante", "category": ACCESSORY_CATEGORY_VIBRANT},
    {"id": "mini_vibro", "label": "Mini-vibro discret", "category": ACCESSORY_CATEGORY_VIBRANT},
    {"id": "masseur_couple", "label": "Masseur pour couple", "category": ACCESSORY_CATEGORY_VIBRANT},

    {"id": "menottes_douces", "label": "Menottes douces", "category": ACCESSORY_CATEGORY_CONTRAINTE_DOUCE},
    {"id": "corde_bondage_debutant", "label": "Corde de bondage débutant", "category": ACCESSORY_CATEGORY_CONTRAINTE_DOUCE},
    {"id": "fouet_leger", "label": "Fouet léger / palette", "category": ACCESSORY_CATEGORY_CONTRAINTE_DOUCE},

    {"id": "lingerie_fine", "label": "Lingerie fine", "category": ACCESSORY_CATEGORY_LINGERIE},
    {"id": "tenue_legere", "label": "Déguisement sexy", "category": ACCESSORY_CATEGORY_LINGERIE},
    {"id": "masque", "label": "Masque sexy", "category": ACCESSORY_CATEGORY_LINGERIE},


    {"id": "lubrifiant", "label": "Lubrifiant", "category": ACCESSORY_CATEGORY_SOINS},
    {"id": "gel_chauffant", "label": "Gel chauffant / rafraîchissant", "category": ACCESSORY_CATEGORY_SOINS},
    {"id": "preservatifs", "label": "Préservatifs", "category": ACCESSORY_CATEGORY_SOINS},
]

ACCESSORY_LABELS = {item["id"]: item["label"] for item in ACCESSORY_CATALOG}


def accessories_by_category() -> dict[str, list[dict]]:
    """Group the catalog by category, preserving ACCESSORY_CATEGORIES order."""
    grouped: dict[str, list[dict]] = {key: [] for key, _ in ACCESSORY_CATEGORIES}
    for item in ACCESSORY_CATALOG:
        grouped.setdefault(item["category"], []).append(item)
    return grouped
