"""Suggestion catalog for the Duo integration.

Every entry is intentionally written at a suggestive, non-graphic level.
The application proposes a theme and a mood, never an explicit, step by
step description of a sexual act. It is up to the couple to decide, in
the moment and within the limits they set in their own profile, how far
they want to take any given suggestion. No entry here describes, or is
inspired by, a practice with a real physical health risk (breath play,
choking, fisting, gagging...) — pleasure never comes at the cost of
safety, and this catalog is not the place to instruct anything risky.

Each activity carries:
- ``actor_sex`` / ``receiver_sex`` (``homme``, ``femme`` or ``indifferent``):
  the actor is the partner whose turn it is to perform the activity, the
  receiver is the other partner. An activity is only proposed for a given
  turn if the sex of the current actor and receiver matches these fields
  (``indifferent`` always matches).
- ``accessory``: either ``None``, or a dict with a ``required`` flag plus
  either an ``id`` (one specific accessories.py entry) or a ``category``
  (any owned item from that whole accessory category — e.g. any vibrant
  toy, whichever one the couple actually owns). When ``required`` is True
  the activity is only proposed if the couple owns a matching accessory;
  when False it's merely preferred.
- ``position``: an optional generic staging cue (see POSITION_* in
  const.py — lying down, standing, kneeling...), never an act description.
- ``phase``: which moment of the encounter the activity typically belongs
  to (see PHASE_* in const.py). Rule of thumb: still-dressed/early
  stimulation is ``phase_excitation``; kissing, finger or mouth contact on
  erogenous zones (including digital penetration) is
  ``phase_preliminaires``; any intense-penetration action (e.g. with a
  toy) is ``phase_intense``; post-rapport tenderness is
  ``phase_resolution``.
- ``duration_mode``: ``"time"`` (duration_min/duration_max, in minutes,
  capped at MAX_ACTIVITY_MINUTES so nothing drags on) or ``"count"``
  (count_min/count_max repetitions of count_unit, e.g. "10 baisers") —
  set through the ``_activity()`` builder below, never by hand.
"""

from .const import (
    CATEGORY_COMMUNICATION,
    CATEGORY_INTENSITE_PLUS,
    CATEGORY_JEU_DE_ROLE,
    CATEGORY_MASSAGE,
    CATEGORY_PRELIMINAIRES,
    CATEGORY_RESOLUTION,
    CATEGORY_SENSORIEL,
    MAX_ACTIVITY_MINUTES,
    PHASE_EXCITATION,
    PHASE_INTENSE,
    PHASE_PRELIMINAIRES,
    PHASE_RESOLUTION,
    POSITION_ALLONGE,
    POSITION_ASSIS,
    POSITION_DEBOUT,
    POSITION_GENOUX,
    POSITION_PENCHE_AVANT,
    POSITION_QUATRE_PATTES,
    SEX_HOMME,
    SEX_INDIFFERENT,
)


def _accessory_id(accessory_id: str, required: bool = True) -> dict:
    return {"id": accessory_id, "required": required}


def _accessory_category(category: str, required: bool = False) -> dict:
    return {"category": category, "required": required}


def _activity(
    activity_id: str,
    category: str,
    phase: str,
    name: str,
    description: str,
    intensity: int,
    *,
    duration: tuple[float, float] | None = None,
    count: tuple[int, int, str] | None = None,
    accessory: dict | None = None,
    position: str | None = None,
    actor_sex: str = SEX_INDIFFERENT,
    receiver_sex: str = SEX_INDIFFERENT,
) -> dict:
    if (duration is None) == (count is None):
        raise ValueError(f"{activity_id}: set exactly one of duration= or count=")

    if duration is not None:
        duration_min, duration_max = duration
        if duration_max > MAX_ACTIVITY_MINUTES:
            raise ValueError(
                f"{activity_id}: duration_max={duration_max} exceeds "
                f"MAX_ACTIVITY_MINUTES={MAX_ACTIVITY_MINUTES}"
            )
        mode_fields = {
            "duration_mode": "time",
            "duration_min": duration_min,
            "duration_max": duration_max,
            "count_min": None,
            "count_max": None,
            "count_unit": None,
        }
    else:
        count_min, count_max, count_unit = count
        mode_fields = {
            "duration_mode": "count",
            "duration_min": None,
            "duration_max": None,
            "count_min": count_min,
            "count_max": count_max,
            "count_unit": count_unit,
        }

    return {
        "id": activity_id,
        "category": category,
        "phase": phase,
        "name": name,
        "description": description,
        "intensity": intensity,
        "accessory": accessory,
        "position": position,
        "actor_sex": actor_sex,
        "receiver_sex": receiver_sex,
        **mode_fields,
    }


ACTIVITIES = [
    # ------------------------------------------------------------------
    # Phase 1 — Excitation : encore habillés, on commence à se stimuler.
    # ------------------------------------------------------------------
    _activity(
        "excitation_baiser_prolonge", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Baiser prolongé",
        "Un baiser qui dure aussi longtemps que vous le souhaitez, sans se presser.",
        1, duration=(2, 3),
    ),
    _activity(
        "excitation_compliment", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Compliment chuchoté",
        "Chuchotez à l'oreille de votre partenaire ce que vous appréciez le plus chez lui/elle ce soir.",
        1, duration=(1, 2),
    ),
    _activity(
        "excitation_striptease", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Effeuillage lent",
        "Un déshabillage joueur et sans précipitation, chacun son tour.",
        2, duration=(2, 3),
    ),
    _activity(
        "excitation_massage_huile", CATEGORY_MASSAGE, PHASE_EXCITATION,
        "Massage à l'huile",
        "Un massage sensuel à l'huile, en silence ou en musique, à tour de rôle.",
        2, count=(15, 30, "mouvements de massage"),
        accessory=_accessory_id("huile de massage", required=True),
    ),
    _activity(
        "excitation_massage_dos", CATEGORY_MASSAGE, PHASE_EXCITATION,
        "Détente du dos",
        "Concentrez le massage sur le dos et la nuque, pour faire redescendre la pression avant la suite.",
        1, count=(10, 20, "mouvements sur le dos"),
    ),
    _activity(
        "excitation_jeu_de_role_rencontre", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Rencontre inconnue",
        "Imaginez, le temps d'une soirée, que vous vous rencontrez pour la première fois.",
        3, duration=(2, 3),
    ),
    _activity(
        "excitation_jeu_de_role_scenario", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Scénario au choix",
        "Chacun propose un petit scénario à jouer ensemble ce soir, sans détails imposés à l'avance.",
        3, duration=(2, 3),
        accessory=_accessory_id("kit_jeu_de_role", required=False),
    ),
    _activity(
        "excitation_jeu_de_role_metier", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Jeu de rôle métier",
        "Incarnez un métier ou un personnage de votre choix, sans script imposé, pour casser la routine.",
        3, duration=(2, 3),
        accessory=_accessory_id("kit_jeu_de_role", required=False),
    ),
    _activity(
        "excitation_communication_fantasme", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Confession d'un fantasme",
        "Partagez un fantasme que vous n'avez encore jamais essayé ensemble.",
        1, duration=(2, 3),
    ),
    _activity(
        "excitation_communication_question_torride", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Question intime",
        "Piochez une question intime à laquelle répondre honnêtement, à tour de rôle.",
        1, duration=(2, 3),
        accessory=_accessory_id("cartes_jeu_couple", required=False),
    ),
    _activity(
        "excitation_communication_liste_envies", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Liste à deux",
        "Complétez ensemble une liste de choses que vous aimeriez essayer un jour.",
        1, duration=(2, 3),
    ),
    _activity(
        "excitation_message_envie", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Message qui donne envie",
        "Envoyez à votre partenaire un message qui donne envie, à lire au moment choisi.",
        1, duration=(1, 2),
    ),
    _activity(
        "excitation_video_inspire", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Contenu qui inspire",
        "Choisissez ensemble un contenu qui vous inspire et regardez-le un moment avant de continuer.",
        2, duration=(2, 3),
    ),
    _activity(
        "excitation_habillage_sur_mesure", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Habillage sur mesure",
        "Un partenaire va se préparer avec la tenue de son choix pendant que l'autre patiente.",
        2, duration=(2, 3),
        accessory=_accessory_id("lingerie_fine", required=False),
    ),
    _activity(
        "excitation_des_du_desir", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Lancer de dés",
        "Lancez les dés du désir et laissez le hasard proposer un thème pour la suite.",
        2, duration=(1, 2),
        accessory=_accessory_id("des_du_desir", required=True),
    ),
    _activity(
        "excitation_jeu_societe", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Jeu de société",
        "Sortez votre jeu de société coquin et jouez une manche avant de continuer.",
        2, duration=(2, 3),
        accessory=_accessory_id("jeu_societe_coquin", required=True),
    ),

    # ------------------------------------------------------------------
    # Phase 2 — Préliminaires : contacts avec les zones érogènes.
    # ------------------------------------------------------------------
    _activity(
        "preliminaires_caresses_guidees", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Caresses guidées",
        "Guidez la main de votre partenaire là où vous aimeriez être touché(e) ce soir.",
        2, duration=(2, 3),
    ),
    _activity(
        "preliminaires_bandeau", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Bandeau surprise",
        "Les yeux bandés, laissez votre partenaire vous surprendre par le toucher.",
        3, duration=(2, 3),
        accessory=_accessory_id("bandeau", required=True),
    ),
    _activity(
        "preliminaires_glacon", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Glaçon et chaleur",
        "Alternez des sensations froides et chaudes sur la peau, doucement.",
        3, duration=(2, 3),
        accessory=_accessory_id("glaçons", required=True),
    ),
    _activity(
        "preliminaires_plume", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Plume et duvet",
        "Des caresses très légères, du bout d'une plume, sur les zones les plus sensibles.",
        2, count=(10, 20, "caresses de plume"),
        accessory=_accessory_id("plume", required=True),
    ),
    _activity(
        "preliminaires_consigne_du_soir", CATEGORY_JEU_DE_ROLE, PHASE_PRELIMINAIRES,
        "Consigne du soir",
        "L'un donne une consigne simple à suivre, l'autre est toujours libre de l'accepter ou non.",
        3, duration=(2, 3),
    ),
    _activity(
        "preliminaires_baisers_comptes", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Baisers comptés",
        "Offrez un nombre convenu de baisers sur les zones sensibles du visage et du cou.",
        2, count=(5, 15, "baisers"),
    ),
    _activity(
        "preliminaires_foulard_guide", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Foulard guide",
        "Utilisez un foulard pour guider délicatement la main de votre partenaire vers ce que vous aimez.",
        3, duration=(2, 3),
        accessory=_accessory_id("foulards", required=True),
    ),
    _activity(
        "preliminaires_attention_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Attention particulière",
        "Explorez avec la bouche les zones que votre partenaire aime, à son rythme.",
        3, duration=(2, 3),
    ),
    _activity(
        "preliminaires_nuque_epaules", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Nuque et épaules",
        "Un enchaînement de baisers ou de caresses sur la nuque et les épaules.",
        2, count=(5, 12, "gestes"),
    ),
    _activity(
        "preliminaires_massage_mains", CATEGORY_MASSAGE, PHASE_PRELIMINAIRES,
        "Mains et poignets",
        "Des caresses sur les mains et les poignets, en remontant doucement vers les bras.",
        2, count=(10, 20, "caresses"),
    ),
    _activity(
        "preliminaires_torse_contre_torse", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Peau contre peau",
        "Rapprochez-vous peau contre peau, sans autre geste, pendant quelques instants.",
        2, duration=(2, 3),
    ),
    _activity(
        "preliminaires_bougie_chaleur", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Chaleur de bougie",
        "Utilisez la cire tiède de la bougie de massage pour une caresse chaude.",
        3, duration=(2, 3),
        accessory=_accessory_id("bougie de massage", required=True),
    ),
    _activity(
        "preliminaires_pieds", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Attention aux pieds",
        "Un massage ou des caresses sur les pieds, pour une sensibilité différente.",
        2, count=(10, 20, "caresses"),
    ),

    # ------------------------------------------------------------------
    # Phase 3 — Intense : actions avec pénétration intense.
    # ------------------------------------------------------------------
    _activity(
        "intense_carte_blanche", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Carte blanche",
        "Le partenaire dont c'est le tour prend l'initiative et fait monter la température, dans le respect des limites fixées dans votre profil.",
        5, duration=(2, 3),
    ),
    _activity(
        "intense_nouveaute", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Nouveauté assumée",
        "Retentez, à deux, quelque chose que vous aviez décliné auparavant — uniquement si vous en avez tous les deux réellement envie ce soir.",
        4, duration=(2, 3),
    ),
    _activity(
        "intense_negociation", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "À négocier ensemble",
        "Discutez ensemble de quelque chose de nouveau à essayer ce soir, et mettez-vous d'accord avant de vous lancer.",
        4, duration=(2, 3),
    ),
    _activity(
        "intense_rythme", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Défi de rythme",
        "Alternez qui mène le rythme du moment, en changeant à chaque sonnerie du minuteur.",
        5, duration=(2, 3),
    ),
    _activity(
        "intense_accessoire_vibrant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Accessoire à deux",
        "Intégrez ensemble l'accessoire vibrant que vous possédez, au rythme et à l'intensité qui vous conviennent.",
        5, duration=(2, 3),
        accessory=_accessory_category("vibrant", required=False),
    ),
    _activity(
        "intense_rythme_lent", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Ralenti assumé",
        "Ralentissez consciemment chaque geste, sans chercher à accélérer.",
        3, duration=(2, 3),
    ),
    _activity(
        "intense_instant_rapide", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Instant bref",
        "Un moment bref et intense, sans préambule, pour changer du rythme habituel.",
        5, duration=(1, 2),
    ),
    _activity(
        "intense_discipline_legere", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Discipline légère",
        "Ajoutez une touche de discipline légère avec l'accessoire choisi, à l'intensité validée ensemble avant de commencer.",
        4, duration=(1, 2),
        accessory=_accessory_id("fouet_leger", required=False),
    ),
    _activity(
        "intense_liens_du_soir", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Liens du soir",
        "Utilisez des liens doux pour immobiliser gentiment votre partenaire, avec un mot d'arrêt clair et respecté.",
        4, duration=(2, 3),
        accessory=_accessory_id("menottes_douces", required=False),
    ),
    _activity(
        "intense_gel_chauffant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Chaleur qui monte",
        "Appliquez le gel chauffant choisi et laissez la sensation s'installer avant de continuer.",
        3, duration=(1, 2),
        accessory=_accessory_id("gel_chauffant", required=False),
    ),
    _activity(
        "intense_confort_lubrifiant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Confort avant tout",
        "Prenez un instant pour appliquer du lubrifiant si besoin : le confort d'abord.",
        1, duration=(1, 1),
        accessory=_accessory_id("lubrifiant", required=False),
    ),
    _activity(
        "intense_protection", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Protection avant tout",
        "Prenez un instant, ensemble, pour la protection si besoin.",
        1, duration=(1, 1),
        accessory=_accessory_id("preservatifs", required=False),
        actor_sex=SEX_HOMME,
    ),
    _activity(
        "intense_position_allonge", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : allongé(e)",
        "Installez-vous allongés, comme vous le sentez sur le moment.",
        4, duration=(1, 2), position=POSITION_ALLONGE,
    ),
    _activity(
        "intense_position_quatre_pattes", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : à quatre pattes",
        "Changez pour la position à quatre pattes, à votre rythme.",
        4, duration=(1, 2), position=POSITION_QUATRE_PATTES,
    ),
    _activity(
        "intense_position_penche_avant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : penché(e) en avant",
        "Essayez la position penché(e) en avant, appuyé(e) sur le lit ou un meuble stable.",
        4, duration=(1, 2), position=POSITION_PENCHE_AVANT,
    ),
    _activity(
        "intense_position_debout", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : debout",
        "Passez à une position debout, contre un support stable.",
        4, duration=(1, 2), position=POSITION_DEBOUT,
    ),
    _activity(
        "intense_position_assis", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : assis(e)",
        "Essayez une position assise, sur une chaise ou le bord du lit.",
        4, duration=(1, 2), position=POSITION_ASSIS,
    ),
    _activity(
        "intense_position_genoux", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : à genoux",
        "Passez à une position à genoux, au sol ou sur le lit.",
        4, duration=(1, 2), position=POSITION_GENOUX,
    ),

    # ------------------------------------------------------------------
    # Phase 4 — Résolution : retour au calme, tendresse après le rapport.
    # ------------------------------------------------------------------
    _activity(
        "resolution_calin_silencieux", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Câlin silencieux",
        "Restez enlacés, sans un mot, juste pour profiter de la proximité.",
        1, duration=(2, 3),
    ),
    _activity(
        "resolution_mot_doux", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Mot doux de fin",
        "Dites-vous, chacun à votre tour, un moment que vous avez particulièrement aimé ce soir.",
        1, duration=(2, 3),
    ),
    _activity(
        "resolution_petite_attention", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Petite attention",
        "Prenez soin l'un de l'autre : un verre d'eau, une couverture, une caresse pour revenir doucement.",
        1, duration=(2, 3),
    ),
    _activity(
        "resolution_verre_partage", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Verre partagé",
        "Partagez un verre d'eau ou une boisson fraîche, blottis l'un contre l'autre.",
        1, duration=(2, 3),
    ),
    _activity(
        "resolution_douche_bain", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Douche ou bain à deux",
        "Terminez la soirée ensemble sous la douche ou dans un bain, sans autre objectif que la détente.",
        1, duration=(2, 3),
    ),
    _activity(
        "resolution_debrief", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Debrief à deux",
        "Discutez de ce que vous referiez, et de ce que vous garderiez pour la prochaine fois.",
        1, duration=(2, 3),
    ),
]


def get_activity(activity_id: str) -> dict | None:
    """Return the activity matching the given id, if any."""
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            return activity
    return None
