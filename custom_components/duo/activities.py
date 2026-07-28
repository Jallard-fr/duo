"""Suggestion catalog for the Duo integration.

Every entry is intentionally written at a suggestive, non-graphic level.
The application proposes a theme and a mood, never an explicit, step by
step description of a sexual act. It is up to the couple to decide, in
the moment and within the limits they set in their own profile, how far
they want to take any given suggestion.

Each activity carries:
- ``actor_sex`` / ``receiver_sex`` (``homme``, ``femme`` or ``indifferent``):
  the actor is the partner whose turn it is to perform the activity, the
  receiver is the other partner. An activity is only proposed for a given
  turn if the sex of the current actor and receiver matches these fields
  (``indifferent`` always matches). The catalog ships with every entry set
  to ``indifferent`` on both fields, since the content stays intentionally
  non-explicit; edit these values if you want specific suggestions to only
  apply to certain combinations of partner sexes.
- ``accessory``: either ``None``, or a dict ``{"id": <accessory id from
  accessories.py>, "required": <bool>}``. When ``required`` is True the
  activity is only proposed if the couple owns that accessory; when False
  it is merely preferred (the activity still works without it, so it's
  just deprioritized rather than excluded when missing).
- ``phase``: which moment of the encounter the activity typically belongs
  to (see PHASE_* in const.py) — a couple can ask for a suggestion for a
  specific phase to accompany how the moment naturally progresses.
  Rule of thumb when adding new entries: still-dressed/early stimulation
  is ``phase_excitation``; kissing, finger or mouth contact on erogenous
  zones (including digital penetration) is ``phase_preliminaires``; any
  intense-penetration action (e.g. with a vibrant toy) is ``phase_intense``;
  post-rapport tenderness is ``phase_resolution``.
"""

from .const import (
    CATEGORY_COMMUNICATION,
    CATEGORY_INTENSITE_PLUS,
    CATEGORY_JEU_DE_ROLE,
    CATEGORY_MASSAGE,
    CATEGORY_PRELIMINAIRES,
    CATEGORY_RESOLUTION,
    CATEGORY_SENSORIEL,
    PHASE_EXCITATION,
    PHASE_INTENSE,
    PHASE_PRELIMINAIRES,
    PHASE_RESOLUTION,
    SEX_INDIFFERENT,
)


def _accessory(accessory_id: str, required: bool = True) -> dict:
    return {"id": accessory_id, "required": required}


# intensity: 1 (très doux) -> 5 (torride)
ACTIVITIES = [
    {
        "id": "preliminaires_baiser",
        "category": CATEGORY_PRELIMINAIRES,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Baiser prolongé",
        "description": "Un baiser qui dure aussi longtemps que vous le souhaitez, sans se presser.",
        "intensity": 1,
        "duration_min": 2,
        "duration_max": 10,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "preliminaires_compliment",
        "category": CATEGORY_PRELIMINAIRES,
        "phase": PHASE_EXCITATION,
        "name": "Compliment chuchoté",
        "description": "Chuchotez à l'oreille de votre partenaire ce que vous appréciez le plus chez lui/elle ce soir.",
        "intensity": 1,
        "duration_min": 2,
        "duration_max": 5,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "preliminaires_caresses_guidees",
        "category": CATEGORY_PRELIMINAIRES,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Caresses guidées",
        "description": "Guidez la main de votre partenaire là où vous aimeriez être touché(e) ce soir.",
        "intensity": 2,
        "duration_min": 3,
        "duration_max": 10,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "preliminaires_striptease",
        "category": CATEGORY_PRELIMINAIRES,
        "phase": PHASE_EXCITATION,
        "name": "Effeuillage lent",
        "description": "Un déshabillage joueur et sans précipitation, chacun son tour.",
        "intensity": 2,
        "duration_min": 3,
        "duration_max": 8,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "sensoriel_bandeau",
        "category": CATEGORY_SENSORIEL,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Bandeau surprise",
        "description": "Les yeux bandés, laissez votre partenaire vous surprendre par le toucher.",
        "intensity": 3,
        "duration_min": 5,
        "duration_max": 15,
        "accessory": _accessory("bandeau", required=True),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "sensoriel_glacon",
        "category": CATEGORY_SENSORIEL,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Glaçon et chaleur",
        "description": "Alternez des sensations froides et chaudes sur la peau, doucement.",
        "intensity": 3,
        "duration_min": 5,
        "duration_max": 10,
        "accessory": _accessory("glaçons", required=True),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "sensoriel_plume",
        "category": CATEGORY_SENSORIEL,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Plume et duvet",
        "description": "Des caresses très légères, du bout d'une plume, sur les zones les plus sensibles.",
        "intensity": 2,
        "duration_min": 5,
        "duration_max": 10,
        "accessory": _accessory("plume", required=True),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "massage_huile",
        "category": CATEGORY_MASSAGE,
        "phase": PHASE_EXCITATION,
        "name": "Massage à l'huile",
        "description": "Un massage sensuel à l'huile, en silence ou en musique, à tour de rôle.",
        "intensity": 2,
        "duration_min": 10,
        "duration_max": 20,
        "accessory": _accessory("huile de massage", required=True),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "massage_dos",
        "category": CATEGORY_MASSAGE,
        "phase": PHASE_EXCITATION,
        "name": "Détente du dos",
        "description": "Concentrez le massage sur le dos et la nuque, pour faire redescendre la pression avant la suite.",
        "intensity": 1,
        "duration_min": 5,
        "duration_max": 15,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "jeu_de_role_rencontre",
        "category": CATEGORY_JEU_DE_ROLE,
        "phase": PHASE_EXCITATION,
        "name": "Rencontre inconnue",
        "description": "Imaginez, le temps d'une soirée, que vous vous rencontrez pour la première fois.",
        "intensity": 3,
        "duration_min": 10,
        "duration_max": 20,
        "accessory": _accessory("tenue_legere", required=False),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "jeu_de_role_scenario",
        "category": CATEGORY_JEU_DE_ROLE,
        "phase": PHASE_EXCITATION,
        "name": "Scénario au choix",
        "description": "Chacun propose un petit scénario à jouer ensemble ce soir, sans détails imposés à l'avance.",
        "intensity": 3,
        "duration_min": 10,
        "duration_max": 20,
        "accessory": _accessory("kit_jeu_de_role", required=False),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "jeu_de_role_ordres_doux",
        "category": CATEGORY_JEU_DE_ROLE,
        "phase": PHASE_PRELIMINAIRES,
        "name": "Consigne du soir",
        "description": "L'un donne une consigne simple à suivre, l'autre est toujours libre de l'accepter ou non.",
        "intensity": 3,
        "duration_min": 5,
        "duration_max": 15,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "communication_fantasme",
        "category": CATEGORY_COMMUNICATION,
        "phase": PHASE_EXCITATION,
        "name": "Confession d'un fantasme",
        "description": "Partagez un fantasme que vous n'avez encore jamais essayé ensemble.",
        "intensity": 1,
        "duration_min": 5,
        "duration_max": 15,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "communication_question_torride",
        "category": CATEGORY_COMMUNICATION,
        "phase": PHASE_EXCITATION,
        "name": "Question intime",
        "description": "Piochez une question intime à laquelle répondre honnêtement, à tour de rôle.",
        "intensity": 1,
        "duration_min": 5,
        "duration_max": 10,
        "accessory": _accessory("cartes_jeu_couple", required=False),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "communication_liste_envies",
        "category": CATEGORY_COMMUNICATION,
        "phase": PHASE_EXCITATION,
        "name": "Liste à deux",
        "description": "Complétez ensemble une liste de choses que vous aimeriez essayer un jour.",
        "intensity": 1,
        "duration_min": 5,
        "duration_max": 15,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "intensite_carte_blanche",
        "category": CATEGORY_INTENSITE_PLUS,
        "phase": PHASE_INTENSE,
        "name": "Carte blanche",
        "description": "Le partenaire dont c'est le tour prend l'initiative et fait monter la température, dans le respect des limites fixées dans votre profil.",
        "intensity": 5,
        "duration_min": 10,
        "duration_max": 30,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "intensite_nouveaute",
        "category": CATEGORY_INTENSITE_PLUS,
        "phase": PHASE_INTENSE,
        "name": "Nouveauté assumée",
        "description": "Retentez, à deux, quelque chose que vous aviez décliné auparavant — uniquement si vous en avez tous les deux réellement envie ce soir.",
        "intensity": 4,
        "duration_min": 10,
        "duration_max": 25,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "intensite_negociation",
        "category": CATEGORY_INTENSITE_PLUS,
        "phase": PHASE_INTENSE,
        "name": "À négocier ensemble",
        "description": "Discutez ensemble de quelque chose de nouveau à essayer ce soir, et mettez-vous d'accord avant de vous lancer.",
        "intensity": 4,
        "duration_min": 10,
        "duration_max": 30,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "intensite_rythme",
        "category": CATEGORY_INTENSITE_PLUS,
        "phase": PHASE_INTENSE,
        "name": "Défi de rythme",
        "description": "Alternez qui mène le rythme du moment, en changeant à chaque sonnerie du minuteur.",
        "intensity": 5,
        "duration_min": 10,
        "duration_max": 20,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "intensite_accessoire_vibrant",
        "category": CATEGORY_INTENSITE_PLUS,
        "phase": PHASE_INTENSE,
        "name": "Accessoire à deux",
        "description": "Intégrez ensemble l'accessoire vibrant de votre choix, au rythme et à l'intensité qui vous conviennent.",
        "intensity": 5,
        "duration_min": 10,
        "duration_max": 25,
        "accessory": _accessory("vibromasseur", required=False),
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "resolution_calin_silencieux",
        "category": CATEGORY_RESOLUTION,
        "phase": PHASE_RESOLUTION,
        "name": "Câlin silencieux",
        "description": "Restez enlacés, sans un mot, juste pour profiter de la proximité aussi longtemps que vous le souhaitez.",
        "intensity": 1,
        "duration_min": 5,
        "duration_max": 20,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "resolution_mot_doux",
        "category": CATEGORY_RESOLUTION,
        "phase": PHASE_RESOLUTION,
        "name": "Mot doux de fin",
        "description": "Dites-vous, chacun à votre tour, un moment que vous avez particulièrement aimé ce soir.",
        "intensity": 1,
        "duration_min": 3,
        "duration_max": 10,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
    {
        "id": "resolution_petite_attention",
        "category": CATEGORY_RESOLUTION,
        "phase": PHASE_RESOLUTION,
        "name": "Petite attention",
        "description": "Prenez soin l'un de l'autre : un verre d'eau, une couverture, une caresse pour revenir doucement.",
        "intensity": 1,
        "duration_min": 3,
        "duration_max": 15,
        "accessory": None,
        "actor_sex": SEX_INDIFFERENT,
        "receiver_sex": SEX_INDIFFERENT,
    },
]


def get_activity(activity_id: str) -> dict | None:
    """Return the activity matching the given id, if any."""
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            return activity
    return None
