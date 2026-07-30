"""Suggestion catalog for the Duo integration.

Entries name a theme or an act plainly enough to match the couple's own
"Questionnaire de limites" vocabulary (fellation, cunnilingus, doigtage,
discipline légère, liens...) rather than staying deliberately vague about
what's on offer — but never turn into a graphic, step-by-step technique
guide. It is up to the couple to decide, in the moment and within the
limits they set in their own profile, how far they want to take any given
suggestion. No entry here describes, or is inspired by, a practice with a
real physical health risk (breath play, choking, fisting, gagging...) —
pleasure never comes at the cost of safety, and this catalog is not the
place to instruct anything risky.

Each activity carries:
- ``actor_sex`` / ``receiver_sex`` (``homme``, ``femme`` or ``indifferent``):
  the actor is the partner whose turn it is to perform the activity, the
  receiver is the other partner. An activity is only proposed for a given
  turn if the sex of the current actor and receiver matches these fields
  (``indifferent`` always matches).
- ``description``: written in the third person, using the ``{actor}`` and
  ``{receiver}`` placeholders wherever a partner needs naming, so the
  frontend can substitute the couple's real, configured first names
  instead of a generic "votre partenaire". The placeholders always follow
  the actor/receiver rule above — never assume the addressee is one or
  the other, read the sentence's actual meaning. Two more placeholders,
  ``{oral_on_receiver}`` and ``{oral_on_actor}``, are filled in by the
  frontend with "une fellation", "un cunnilingus" or the generic "une
  stimulation orale", picked from the sex of whichever of the two is
  actually on the receiving end of that particular sentence (not always
  the receiver — see the "active" tied-hands variants below).
- ``accessory``: either ``None``, or a dict with a ``required`` flag plus
  either an ``id`` (one specific accessories.py entry) or a ``category``
  (any owned item from that whole accessory category — e.g. any vibrant
  toy, whichever one the couple actually owns). When ``required`` is True
  the activity is only proposed if the couple owns a matching accessory;
  when False it's merely preferred. Either way, the resolved accessory
  name is folded into the displayed description text by the frontend, not
  the title.
- ``position``: an optional generic staging cue (see POSITION_* in
  const.py — lying down, standing, kneeling...), never an act description.
- ``phase``: which moment of the encounter the activity typically belongs
  to (see PHASE_* in const.py). Rule of thumb: still-dressed/early
  stimulation is ``phase_excitation``; kissing, finger or mouth contact on
  erogenous zones (including digital penetration) is
  ``phase_preliminaires``; any intense-penetration action (e.g. with a
  toy) is ``phase_intense``; post-rapport tenderness is
  ``phase_resolution``.
- ``duration_mode``: ``"time"`` (a single, fixed ``duration_minutes``,
  capped at MAX_ACTIVITY_MINUTES so nothing drags on) or ``"count"`` (a
  single, fixed ``count`` of ``count_unit``, e.g. "10 baisers") — set
  through the ``_activity()`` builder below, never by hand. Durations are
  intentionally fixed rather than randomised: the couple should be able
  to anticipate how long an activity will run before accepting it.
- ``practice``: optional PRACTICE_* tag (const.py) linking an activity to
  one of the couple's closed-question consent limits (see the card's
  "Questionnaire de limites"). The actor is considered to "donne" that
  practice, the receiver to "recoit" it (except PRACTICE_JOUETS, which is
  symmetric — "usage"). A "non" answer from either partner in the
  relevant role excludes the activity, unless that partner has enabled
  "braver ses interdits".
- ``practices``: like ``practice``, but for activities that need more than
  one tag checked at once, or where the actor isn't always the one who
  "donne". A list of ``(practice, role)`` pairs, ``role`` being ``"donne"``,
  ``"recoit"`` or ``"usage"``. Used by the tied-hands "active" variants
  below, where the tied partner is the one performing oral on the actor —
  there, the oral tag is ``(PRACTICE_ORAL, "recoit")`` from the actor's own
  point of view, alongside the restraint tag ``(PRACTICE_LIENS, "donne")``.
  PRACTICE_ANAL has no tagged entry yet since nothing in this catalog is
  anal-specific — the couple's answer is still recorded for future use.
- ``intense_stage``: ``None``, ``"first"``, ``"early"`` or ``"late"`` —
  splits ``phase_intense`` into the 4-tour progression described in
  const.py (see PHASE_TARGET_COUNTS / INTENSE_TARGET_COUNT): ``"first"``
  acts (doigtage intense) are only proposed on tour 1, ``"early"`` acts
  (sexe oral, jouet vibrant, fessée légère) only on tours 1-2, ``"late"``
  acts (positions nommées) only on tours 3-4. ``None`` means the activity
  isn't part of that progression and stays proposable throughout the phase.
- ``once_per_phase``: ``None``, or a group key (e.g. ``"oral"``,
  ``"doigtage_intense"``, ``"fessee_intense"``) shared by every variant of
  that act. Once one variant of a given group has been accepted for a
  given receveur·se, on ``phase_preliminaires`` or ``phase_intense``, no
  other activity of that same group is proposed again to that receveur·se
  for the rest of that phase this session — a soft cap ("at most once"),
  never a guarantee ("at least once"): nothing forces it to happen.
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
    PRACTICE_DISCIPLINE,
    PRACTICE_JOUETS,
    PRACTICE_LIENS,
    PRACTICE_ORAL,
    SEX_FEMME,
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
    duration: float | None = None,
    count: tuple[int, str] | None = None,
    accessory: dict | None = None,
    position: str | None = None,
    practice: str | None = None,
    practices: list[tuple[str, str]] | None = None,
    penetration: bool = False,
    actor_sex: str = SEX_INDIFFERENT,
    receiver_sex: str = SEX_INDIFFERENT,
    intense_stage: str | None = None,
    once_per_phase: str | None = None,
) -> dict:
    if (duration is None) == (count is None):
        raise ValueError(f"{activity_id}: set exactly one of duration= or count=")

    if duration is not None:
        if duration > MAX_ACTIVITY_MINUTES:
            raise ValueError(
                f"{activity_id}: duration={duration} exceeds "
                f"MAX_ACTIVITY_MINUTES={MAX_ACTIVITY_MINUTES}"
            )
        mode_fields = {
            "duration_mode": "time",
            "duration_minutes": duration,
            "count": None,
            "count_unit": None,
        }
    else:
        count_value, count_unit = count
        mode_fields = {
            "duration_mode": "count",
            "duration_minutes": None,
            "count": count_value,
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
        "practice": practice,
        "practices": practices,
        "penetration": penetration,
        "actor_sex": actor_sex,
        "receiver_sex": receiver_sex,
        "intense_stage": intense_stage,
        "once_per_phase": once_per_phase,
        **mode_fields,
    }


ACTIVITIES = [
    # ------------------------------------------------------------------
    # Phase 1 — Excitation : encore habillés, on commence à se stimuler.
    # ------------------------------------------------------------------
    _activity(
        "excitation_baiser_prolonge", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Baiser prolongé",
        "{actor} et {receiver} échangent un baiser prolongé, sans se presser.",
        1, duration=2,
    ),
    _activity(
        "excitation_compliment", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Compliment chuchoté",
        "{actor} chuchote à l'oreille de {receiver} ce que {actor} apprécie le plus chez {receiver} ce soir.",
        1, duration=1,
    ),
    _activity(
        "excitation_striptease", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Effeuillage lent",
        "{actor} se déshabille lentement et avec espièglerie pour {receiver}, sans précipitation.",
        2, duration=3,
    ),
    _activity(
        "excitation_massage_huile", CATEGORY_MASSAGE, PHASE_EXCITATION,
        "Massage à l'huile",
        "{actor} offre à {receiver} un massage sensuel à l'huile, en silence ou en musique.",
        2, count=(20, "mouvements de massage"),
        accessory=_accessory_id("huile de massage", required=True),
    ),
    _activity(
        "excitation_massage_dos", CATEGORY_MASSAGE, PHASE_EXCITATION,
        "Détente du dos",
        "{actor} concentre le massage sur le dos et la nuque de {receiver}, pour faire redescendre la pression avant la suite.",
        1, count=(15, "mouvements sur le dos"),
    ),
    _activity(
        "excitation_jeu_de_role_rencontre", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Rencontre inconnue",
        "{actor} et {receiver} imaginent, le temps d'une soirée, qu'ils se rencontrent pour la première fois.",
        3, duration=3,
    ),
    _activity(
        "excitation_jeu_de_role_scenario", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Scénario au choix",
        "{actor} et {receiver} proposent chacun un petit scénario à jouer ensemble ce soir, sans détails imposés à l'avance.",
        3, duration=3,
        accessory=_accessory_id("kit_jeu_de_role", required=False),
    ),
    _activity(
        "excitation_jeu_de_role_metier", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Jeu de rôle métier",
        "{actor} incarne, pour {receiver}, un métier ou un personnage de son choix, sans script imposé, pour casser la routine.",
        3, duration=3,
        accessory=_accessory_id("kit_jeu_de_role", required=False),
    ),
    _activity(
        "excitation_communication_fantasme", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Confession d'un fantasme",
        "{actor} partage avec {receiver} un fantasme qu'ils n'ont encore jamais essayé ensemble.",
        1, duration=2,
    ),
    _activity(
        "excitation_communication_question_torride", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Question intime",
        "{actor} et {receiver} piochent une question intime à laquelle répondre honnêtement, chacun à son tour.",
        1, duration=2,
        accessory=_accessory_id("cartes_jeu_couple", required=False),
    ),
    _activity(
        "excitation_communication_liste_envies", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Liste à deux",
        "{actor} et {receiver} complètent ensemble une liste de choses qu'ils aimeraient essayer un jour.",
        1, duration=2,
    ),
    _activity(
        "excitation_message_envie", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Message qui donne envie",
        "{actor} envoie à {receiver} un message qui donne envie, à lire au moment choisi.",
        1, duration=1,
    ),
    _activity(
        "excitation_video_inspire", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Contenu qui inspire",
        "{actor} et {receiver} choisissent ensemble un contenu qui les inspire et le regardent un moment avant de continuer.",
        2, duration=3,
    ),
    _activity(
        "excitation_habillage_sur_mesure", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Habillage sur mesure",
        "{actor} se prépare avec la tenue de son choix pendant que {receiver} patiente.",
        2, duration=3,
        accessory=_accessory_id("lingerie_fine", required=False),
    ),
    _activity(
        "excitation_des_du_desir", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Lancer de dés",
        "{actor} et {receiver} lancent les dés du désir et laissent le hasard proposer un thème pour la suite.",
        2, duration=1,
        accessory=_accessory_id("des_du_desir", required=True),
    ),
    _activity(
        "excitation_jeu_societe", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Jeu de société",
        "{actor} et {receiver} sortent leur jeu de société coquin et jouent une manche avant de continuer.",
        2, duration=3,
        accessory=_accessory_id("jeu_societe_coquin", required=True),
    ),
    _activity(
        "excitation_gage_coquin", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Gage coquin",
        "{actor} propose un gage coquin à {receiver}, qui peut l'accepter ou en proposer un autre à la place.",
        2, duration=2,
        accessory=_accessory_id("cartes_jeu_couple", required=False),
    ),
    _activity(
        "excitation_mot_coquin", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Mot coquin glissé à l'oreille",
        "{actor} glisse à l'oreille de {receiver} une phrase coquine, sans détail, juste de quoi faire monter l'envie.",
        2, duration=1,
    ),
    _activity(
        "excitation_regard_soutenu", CATEGORY_COMMUNICATION, PHASE_EXCITATION,
        "Regard soutenu",
        "{actor} et {receiver} se regardent intensément, en silence, et se laissent approcher lentement l'un de l'autre.",
        1, duration=1,
    ),
    _activity(
        "excitation_danse_collee", CATEGORY_PRELIMINAIRES, PHASE_EXCITATION,
        "Danse collée",
        "{actor} et {receiver} dansent lentement, tout près l'un de l'autre, sur une musique choisie ensemble.",
        2, duration=3,
    ),
    _activity(
        "excitation_compte_a_rebours", CATEGORY_JEU_DE_ROLE, PHASE_EXCITATION,
        "Compte à rebours coquin",
        "{actor} et {receiver} lancent un compte à rebours et s'offrent un geste tendre différent à chaque palier, comme un petit rituel à deux.",
        2, duration=3,
    ),

    # ------------------------------------------------------------------
    # Phase 2 — Préliminaires : contacts avec les zones érogènes.
    # ------------------------------------------------------------------
    _activity(
        "preliminaires_caresses_guidees", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Caresses guidées",
        "{receiver} guide la main de {actor} vers les endroits où {receiver_ref} aimerait être touché{receiver_e} ce soir.",
        2, duration=2,
    ),
    _activity(
        "preliminaires_bandeau", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Bandeau surprise",
        "Les yeux bandés, {receiver} se laisse surprendre par le toucher de {actor}.",
        3, duration=3,
        accessory=_accessory_id("bandeau", required=True),
    ),
    _activity(
        "preliminaires_glacon", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Glaçon et chaleur",
        "{actor} alterne, sur la peau de {receiver}, des sensations froides et chaudes, doucement.",
        3, duration=2,
        accessory=_accessory_id("glaçons", required=True),
    ),
    _activity(
        "preliminaires_plume", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Plume et duvet",
        "{actor} caresse {receiver} très légèrement, du bout d'une plume, sur les zones les plus sensibles.",
        2, count=(15, "caresses de plume"),
        accessory=_accessory_id("plume", required=True),
    ),
    _activity(
        "preliminaires_consigne_du_soir", CATEGORY_JEU_DE_ROLE, PHASE_PRELIMINAIRES,
        "Consigne du soir",
        "{actor} donne une consigne simple à {receiver}, qui reste toujours libre de l'accepter ou non.",
        3, duration=2,
    ),
    _activity(
        "preliminaires_baisers_comptes", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Baisers comptés",
        "{actor} offre à {receiver} un nombre convenu de baisers sur les zones sensibles du visage et du cou.",
        2, count=(10, "baisers"),
    ),
    _activity(
        "preliminaires_foulard_guide", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Foulard guide",
        "Avec un foulard, {receiver} guide délicatement la main de {actor} vers ce que {receiver} aime.",
        3, duration=2,
        accessory=_accessory_id("foulards", required=True),
    ),
    _activity(
        "preliminaires_attention_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Stimulation orale",
        "{actor} fait {oral_on_receiver} à {receiver}, à son rythme et aussi longtemps que {receiver} le souhaite.",
        3, duration=3,
        practice=PRACTICE_ORAL,
    ),
    _activity(
        "preliminaires_doigtage", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Doigtage",
        "{actor} caresse et pénètre doucement {receiver} du bout des doigts, en s'adaptant à ses réactions.",
        4, duration=3,
        receiver_sex=SEX_FEMME,
        penetration=True,
    ),
    _activity(
        "preliminaires_masturbation_manuelle", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Stimulation manuelle",
        "{actor} stimule {receiver} avec la main, en variant le rythme et la pression selon ses réactions.",
        4, duration=3,
        receiver_sex=SEX_HOMME,
    ),
    _activity(
        "preliminaires_stimulation_clitoridienne", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Stimulation clitoridienne",
        "{actor} stimule le clitoris de {receiver} du bout des doigts ou avec l'accessoire vibrant choisi, en variant les mouvements (cercles, va-et-vient, petits carrés) selon ses préférences.",
        4, duration=3,
        receiver_sex=SEX_FEMME,
        accessory=_accessory_category("vibrant", required=False),
    ),
    _activity(
        "preliminaires_jouet_penetration", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Pénétration avec un jouet",
        "{actor} insère délicatement le jouet vibrant choisi et laisse {receiver} s'habituer à la sensation, à son rythme.",
        4, duration=3,
        accessory=_accessory_category("vibrant", required=True),
        penetration=True,
    ),
    _activity(
        "preliminaires_nuque_epaules", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Nuque et épaules",
        "{actor} enchaîne baisers et caresses sur la nuque et les épaules de {receiver}.",
        2, count=(8, "gestes"),
    ),
    _activity(
        "preliminaires_massage_mains", CATEGORY_MASSAGE, PHASE_PRELIMINAIRES,
        "Mains et poignets",
        "{actor} caresse les mains et les poignets de {receiver}, en remontant doucement vers les bras.",
        2, count=(15, "caresses"),
    ),
    _activity(
        "preliminaires_torse_contre_torse", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Peau contre peau",
        "{actor} et {receiver} se rapprochent peau contre peau, sans autre geste, pendant quelques instants.",
        2, duration=2,
    ),
    _activity(
        "preliminaires_bougie_chaleur", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Chaleur de bougie",
        "{actor} utilise la cire tiède de la bougie de massage pour une caresse chaude sur {receiver}.",
        3, duration=2,
        accessory=_accessory_id("bougie de massage", required=True),
    ),
    _activity(
        "preliminaires_pieds", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Attention aux pieds",
        "{actor} masse ou caresse les pieds de {receiver}, pour une sensibilité différente.",
        2, count=(15, "caresses"),
    ),

    # ------------------------------------------------------------------
    # Phase 2 (suite) — Zones érogènes : mêmes zones, déclinées selon la
    # méthode (main, bouche, souffle, objet effleurant) pour multiplier les
    # variantes sans jamais devenir explicite, plus quelques mises en scène
    # (yeux bandés, mains liées ou attachées, fouet léger en effleurement
    # seulement — jamais un coup porté) qui peuvent se combiner à n'importe
    # laquelle des caresses ci-dessus via les accessoires du couple.
    # ------------------------------------------------------------------
    _activity(
        "preliminaires_oreilles_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Lobes sensibles",
        "{actor} embrasse et mordille délicatement les lobes d'oreille de {receiver}.",
        3, count=(10, "baisers sur les lobes"),
    ),
    _activity(
        "preliminaires_oreilles_souffle", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Souffle chaud à l'oreille",
        "{actor} laisse son souffle chaud effleurer l'oreille de {receiver}, tout près, sans un geste.",
        2, duration=1,
    ),
    _activity(
        "preliminaires_cou_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Baisers dans le cou",
        "{actor} embrasse lentement le cou et la gorge de {receiver}.",
        3, count=(12, "baisers dans le cou"),
    ),
    _activity(
        "preliminaires_cou_souffle", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Souffle sur la nuque",
        "{actor} promène son souffle le long du cou de {receiver}, sans le toucher.",
        2, duration=1,
    ),
    _activity(
        "preliminaires_torse_mains", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Caresses sur le torse",
        "{actor} caresse lentement le torse et la poitrine de {receiver}, en variant la pression.",
        3, count=(20, "caresses"),
    ),
    _activity(
        "preliminaires_torse_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Baisers sur la poitrine",
        "{actor} dépose une série de baisers sur la poitrine de {receiver}, à son rythme.",
        3, count=(12, "baisers"),
    ),
    _activity(
        "preliminaires_bas_dos_mains", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Creux des reins",
        "{actor} caresse le bas du dos et le creux des reins de {receiver}, d'un geste lent et appuyé.",
        2, count=(15, "caresses"),
    ),
    _activity(
        "preliminaires_bas_dos_objet", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Effleurement du bas du dos",
        "{actor} effleure le bas du dos de {receiver} avec l'objet choisi, juste assez pour donner des frissons.",
        3, duration=2,
        accessory=_accessory_id("plume", required=False),
    ),
    _activity(
        "preliminaires_cuisses_mains", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Intérieur des cuisses",
        "{actor} remonte lentement les mains le long de l'intérieur des cuisses de {receiver}.",
        4, count=(15, "caresses"),
    ),
    _activity(
        "preliminaires_cuisses_souffle", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Souffle sur les cuisses",
        "{actor} laisse son souffle glisser le long des cuisses de {receiver}, sans les toucher.",
        3, duration=1,
    ),
    _activity(
        "preliminaires_nombril_bouche", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Baisers autour du nombril",
        "{actor} embrasse le ventre et le tour du nombril de {receiver}, en remontant doucement.",
        3, count=(10, "baisers"),
    ),
    _activity(
        "preliminaires_nombril_objet", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Effleurement du ventre",
        "{actor} effleure le ventre de {receiver} avec l'objet choisi, en dessinant des cercles lents.",
        2, duration=2,
        accessory=_accessory_id("plume", required=False),
    ),
    _activity(
        "preliminaires_genoux_mains", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Creux des genoux",
        "{actor} caresse le creux des genoux de {receiver}, une zone sensible souvent oubliée.",
        2, count=(10, "caresses"),
    ),
    _activity(
        "preliminaires_genoux_objet", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Effleurement derrière les genoux",
        "{actor} effleure l'arrière des genoux de {receiver} avec l'objet choisi, pour une sensation inattendue.",
        2, duration=1,
        accessory=_accessory_id("plume", required=False),
    ),
    _activity(
        "preliminaires_vagues_de_plaisir", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Vagues de plaisir",
        "{actor} alterne, avec {receiver}, des moments de stimulation plus intense et des pauses plus douces, pour faire durer l'envie avant d'aller plus loin.",
        3, duration=3,
    ),
    _activity(
        "preliminaires_mains_liees_mobiles", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains liées, mais mobiles",
        "Les mains de {receiver} sont liées ensemble avec des liens doux, mais restent libres de bouger, pendant que {actor} prend les initiatives.",
        3, duration=2,
        accessory=_accessory_id("foulards", required=True),
        practice=PRACTICE_LIENS,
    ),
    _activity(
        "preliminaires_mains_attachees_lit", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains attachées à la tête de lit",
        "{actor} attache doucement les mains de {receiver} à la tête de lit, avec un mot d'arrêt clair et respecté par les deux.",
        4, duration=2,
        accessory=_accessory_id("menottes_douces", required=True),
        practice=PRACTICE_LIENS,
    ),

    # Les deux mises en scène ci-dessus déclinées avec un acte précis plutôt
    # que de simples caresses : doigtage, stimulation manuelle, ou stimulation
    # orale — dans un sens comme dans l'autre, puisque seules les mains sont
    # immobilisées. Dans les variantes "actif", c'est {receiver} (mains
    # liées) qui prend l'initiative avec la bouche sur {actor} : voir
    # ``practices`` dans le docstring du module pour le rôle de consentement
    # inversé que ça implique.
    _activity(
        "preliminaires_mains_liees_doigtage", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains liées, doigtage",
        "Les mains de {receiver} sont liées mais mobiles, pendant que {actor} la caresse et la pénètre doucement du bout des doigts.",
        4, duration=2,
        accessory=_accessory_id("foulards", required=True),
        practice=PRACTICE_LIENS,
        receiver_sex=SEX_FEMME,
        penetration=True,
    ),
    _activity(
        "preliminaires_mains_attachees_doigtage", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains attachées au lit, doigtage",
        "{actor} attache doucement les mains de {receiver} à la tête de lit, puis la caresse et la pénètre du bout des doigts.",
        5, duration=2,
        accessory=_accessory_id("menottes_douces", required=True),
        practice=PRACTICE_LIENS,
        receiver_sex=SEX_FEMME,
        penetration=True,
    ),
    _activity(
        "preliminaires_mains_liees_masturbation", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains liées, stimulation manuelle",
        "Les mains de {receiver} sont liées mais mobiles, pendant que {actor} le stimule avec la main.",
        4, duration=2,
        accessory=_accessory_id("foulards", required=True),
        practice=PRACTICE_LIENS,
        receiver_sex=SEX_HOMME,
    ),
    _activity(
        "preliminaires_mains_attachees_masturbation", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains attachées au lit, stimulation manuelle",
        "{actor} attache doucement les mains de {receiver} à la tête de lit, puis le stimule avec la main.",
        5, duration=2,
        accessory=_accessory_id("menottes_douces", required=True),
        practice=PRACTICE_LIENS,
        receiver_sex=SEX_HOMME,
    ),
    _activity(
        "preliminaires_mains_liees_oral_passive", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains liées, stimulation orale reçue",
        "Les mains de {receiver} sont liées mais mobiles, pendant que {actor} lui fait {oral_on_receiver}.",
        4, duration=2,
        accessory=_accessory_id("foulards", required=True),
        practices=[(PRACTICE_LIENS, "donne"), (PRACTICE_ORAL, "donne")],
    ),
    _activity(
        "preliminaires_mains_attachees_oral_passive", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains attachées au lit, stimulation orale reçue",
        "{actor} attache doucement les mains de {receiver} à la tête de lit, puis lui fait {oral_on_receiver}.",
        5, duration=2,
        accessory=_accessory_id("menottes_douces", required=True),
        practices=[(PRACTICE_LIENS, "donne"), (PRACTICE_ORAL, "donne")],
    ),
    _activity(
        "preliminaires_mains_liees_oral_active", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains liées, stimulation orale offerte",
        "Même mains liées, {receiver} prend l'initiative et fait {oral_on_actor} à {actor}.",
        4, duration=2,
        accessory=_accessory_id("foulards", required=True),
        practices=[(PRACTICE_LIENS, "donne"), (PRACTICE_ORAL, "recoit")],
    ),
    _activity(
        "preliminaires_mains_attachees_oral_active", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Mains attachées au lit, stimulation orale offerte",
        "{actor} attache doucement les mains de {receiver} à la tête de lit ; même ainsi, {receiver} prend l'initiative et fait {oral_on_actor} à {actor}.",
        5, duration=2,
        accessory=_accessory_id("menottes_douces", required=True),
        practices=[(PRACTICE_LIENS, "donne"), (PRACTICE_ORAL, "recoit")],
    ),
    _activity(
        "preliminaires_fouet_effleurement", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Effleurement au fouet léger",
        "{actor} effleure la peau de {receiver} avec le petit fouet, sans jamais frapper — juste pour le contact et le contraste des sensations.",
        3, duration=2,
        accessory=_accessory_id("fouet_leger", required=True),
    ),
    _activity(
        "preliminaires_fouet_surprise", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Fouet léger avec surprise",
        "{actor} effleure la peau de {receiver} avec le petit fouet ; comme {receiver_ref} est partant{receiver_e} pour la discipline légère, {actor_ref} peut aussi y glisser un petit coup de temps en temps, pour surprendre.",
        4, duration=2,
        accessory=_accessory_id("fouet_leger", required=True),
        practice=PRACTICE_DISCIPLINE,
    ),
    _activity(
        "preliminaires_liens_effleurement", CATEGORY_SENSORIEL, PHASE_PRELIMINAIRES,
        "Caresse en liens doux",
        "{actor} fait glisser un lien doux sur la peau de {receiver}, comme une caresse texturée, sans l'attacher.",
        2, duration=2,
        accessory=_accessory_id("foulards", required=False),
    ),

    _activity(
        "preliminaires_confort_lubrifiant", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Confort avant tout",
        "{actor} et {receiver} prennent un instant pour appliquer du lubrifiant si besoin : le confort d'abord.",
        1, duration=1,
        accessory=_accessory_id("lubrifiant", required=False),
    ),
    _activity(
        "preliminaires_protection", CATEGORY_PRELIMINAIRES, PHASE_PRELIMINAIRES,
        "Protection avant tout",
        "{actor} et {receiver} prennent un instant, ensemble, pour la protection si besoin.",
        1, duration=1,
        accessory=_accessory_id("preservatifs", required=False),
        actor_sex=SEX_HOMME,
    ),

    # ------------------------------------------------------------------
    # Phase 3 — Intense : uniquement des positions avec pénétration, une
    # pénétration avec un jouet vibrant, ou du sexe oral en tout début de
    # phase — le couple a explicitement demandé de purifier cette phase à
    # ces 3 catégories, en retirant tout ce qui n'est ni pénétratif ni oral
    # (accessoire non pénétratif, fessée, liens seuls, gel chauffant...).
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Phase 4 — Résolution : retour au calme, tendresse après le rapport.
    # ------------------------------------------------------------------
    _activity(
        "resolution_calin_silencieux", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Câlin silencieux",
        "{actor} et {receiver} restent enlacés, sans un mot, juste pour profiter de la proximité.",
        1, duration=3,
    ),
    _activity(
        "resolution_mot_doux", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Mot doux de fin",
        "{actor} et {receiver} se disent, chacun à leur tour, un moment qu'ils ont particulièrement aimé ce soir.",
        1, duration=2,
    ),
    _activity(
        "resolution_petite_attention", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Petite attention",
        "{actor} prend soin de {receiver} : un verre d'eau, une couverture, une caresse pour revenir doucement.",
        1, duration=2,
    ),
    _activity(
        "resolution_verre_partage", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Verre partagé",
        "{actor} et {receiver} partagent un verre d'eau ou une boisson fraîche, blottis l'un contre l'autre.",
        1, duration=2,
    ),
    _activity(
        "resolution_douche_bain", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Douche ou bain à deux",
        "{actor} et {receiver} terminent la soirée ensemble sous la douche ou dans un bain, sans autre objectif que la détente.",
        1, duration=3,
    ),
    _activity(
        "resolution_debrief", CATEGORY_RESOLUTION, PHASE_RESOLUTION,
        "Debrief à deux",
        "{actor} et {receiver} discutent de ce qu'ils referaient, et de ce qu'ils garderaient pour la prochaine fois.",
        1, duration=3,
    ),
]

# ---------------------------------------------------------------------------
# Variantes de caresses générées : plutôt que de retaper à la main chaque
# combinaison zone × méthode × contrainte × bandeau, on les construit ici à
# partir de quelques tableaux de données — le couple a explicitement demandé
# de multiplier les combinaisons pour que le tirage aléatoire varie beaucoup
# plus souvent. Chaque variante reste au même niveau que les entrées écrites
# à la main ci-dessus (caresse, baiser, morsure légère, souffle, pincement
# léger, effleurement d'un objet) ; seuls la zone et le contexte (mains
# liées ou non, yeux bandés ou non) changent d'une variante à l'autre.
# ---------------------------------------------------------------------------

_CARESS_ZONES = [
    # clé, forme avec article (utilisée avec "de {receiver}"), forme
    # possessive (utilisée quand {receiver} a déjà été nommé·e plus tôt
    # dans la même description, pour ne pas répéter son prénom), titre.
    ("oreilles", "les oreilles", "ses oreilles", "Oreilles"),
    ("cou", "le cou", "son cou", "Cou"),
    ("poitrine", "la poitrine", "sa poitrine", "Poitrine"),
    ("dos", "le bas du dos", "son bas du dos", "Bas du dos"),
    ("cuisses", "l'intérieur des cuisses", "l'intérieur de ses cuisses", "Intérieur des cuisses"),
    ("ventre", "le ventre et le nombril", "son ventre et son nombril", "Ventre"),
    ("genoux", "le creux des genoux", "le creux de ses genoux", "Creux des genoux"),
    ("levres", "les lèvres et le visage", "ses lèvres et son visage", "Lèvres et visage"),
    ("fesses", "les fesses", "ses fesses", "Fesses"),
    ("mains", "les mains et les poignets", "ses mains et ses poignets", "Mains et poignets"),
    ("pieds", "les pieds", "ses pieds", "Pieds"),
]

# clé, catégorie, libellé pour le titre, verbe (juste avant la zone),
# complément final (après "de {receiver}"/la forme possessive, vide si
# aucun), intensité de base, durée de base (minutes).
_CARESS_METHODS = [
    ("main", CATEGORY_PRELIMINAIRES, "Caresses", "caresse", " avec les mains", 2, 2),
    ("bouche", CATEGORY_PRELIMINAIRES, "Baisers", "embrasse", "", 3, 2),
    ("langue", CATEGORY_PRELIMINAIRES, "Coups de langue", "lèche", " du bout de la langue", 3, 2),
    ("souffle", CATEGORY_SENSORIEL, "Souffle", "souffle doucement sur", "", 2, 1),
    ("mordille", CATEGORY_SENSORIEL, "Petites morsures", "mordille légèrement", "", 3, 1),
    ("titille", CATEGORY_SENSORIEL, "Titillations", "titille", " du bout des doigts", 2, 1),
    ("pince", CATEGORY_SENSORIEL, "Pincements légers", "pince délicatement", "", 3, 1),
    ("objet", CATEGORY_SENSORIEL, "Effleurement", "effleure", " avec l'objet choisi", 2, 2),
]

_RESTRAINTS = ["libre", "mobile", "fixe"]
_RESTRAINT_LABELS = {"libre": None, "mobile": "mains liées", "fixe": "mains attachées"}

# Positions génériques (voir POSITION_* dans const.py) réutilisées ici comme
# encore une dimension de variation, en plus de la contrainte et du bandeau
# ci-dessus — le couple a explicitement demandé de multiplier au maximum les
# combinaisons de positions. ``None`` = pas de position précisée (comme
# avant l'ajout de cette dimension). {receiver} a toujours déjà été nommé·e
# plus tôt dans la description à ce stade : on utilise {receiver_ref_cap}
# (un pronom pour un couple hétérosexuel, sinon le prénom répété) plutôt que
# de le/la renommer une deuxième fois — la variante "_cap" porte une
# majuscule car ces clauses démarrent toujours une nouvelle phrase — et
# {receiver_e} pour accorder l'adjectif au féminin le cas échéant (plutôt
# que la notation "(e)").
_CARESS_POSITIONS = [
    (None, None, None),
    (POSITION_ALLONGE, "allongé", "{receiver_ref_cap} est allongé{receiver_e}."),
    (POSITION_QUATRE_PATTES, "à quatre pattes", "{receiver_ref_cap} est à quatre pattes."),
    (
        POSITION_PENCHE_AVANT,
        "penché",
        "{receiver_ref_cap} est penché{receiver_e} en avant, appuyé{receiver_e} sur un meuble ou un mur.",
    ),
    (POSITION_DEBOUT, "debout", "{receiver_ref_cap} est debout."),
    (
        POSITION_ASSIS,
        "assis",
        "{receiver_ref_cap} est assis{receiver_e}, sur une chaise ou le bord du lit.",
    ),
    (POSITION_GENOUX, "à genoux", "{receiver_ref_cap} est à genoux."),
]


def _restraint_intro(restraint: str, blindfold: bool, position: str | None = None) -> str:
    """Phrase d'introduction posant le contexte (liens, bandeau) avant
    l'action elle-même ; vide si ni l'un ni l'autre ne s'applique. Nomme
    {receiver} une seule fois : c'est toujours la première mention de la
    description quand elle est présente. Assis·e, "attaché à un point fixe"
    devient "mains attachées dans le dos" — plus plausible que d'attacher
    la personne à un point fixe alors qu'elle est assise."""
    if restraint == "mobile":
        extra = " et les yeux bandés" if blindfold else ""
        return "{receiver} a les mains liées mais mobiles" + extra + ", pendant que "
    if restraint == "fixe":
        if position == POSITION_ASSIS:
            base = "{receiver} a les mains attachées dans le dos"
        else:
            base = "{receiver} est attaché{receiver_e} à un point fixe"
        extra = ", les yeux bandés," if blindfold else ""
        return base + extra + " pendant que "
    if blindfold:
        return "Les yeux bandés, {receiver} se laisse surprendre pendant que "
    return ""


def _restraint_accessory(restraint: str) -> dict | None:
    if restraint == "mobile":
        return _accessory_id("foulards", required=True)
    if restraint == "fixe":
        return _accessory_id("menottes_douces", required=True)
    return None


def _restraint_label(restraint: str, position: str | None) -> str | None:
    """Libellé de contrainte pour le titre — voir _restraint_intro pour la
    même exception "assis·e"."""
    if restraint == "fixe" and position == POSITION_ASSIS:
        return "mains dans le dos"
    return _RESTRAINT_LABELS[restraint]


def _generate_caress_variants() -> list[dict]:
    variants = []
    for zone_key, zone_article, zone_possessive, zone_title in _CARESS_ZONES:
        for method_key, category, method_title, verb, trailing, base_intensity, base_duration in _CARESS_METHODS:
            for restraint in _RESTRAINTS:
                for blindfold in (False, True):
                    # {receiver} n'est nommé·e qu'une fois : par l'intro liens/
                    # bandeau si elle existe, sinon par l'action elle-même
                    # (qui utilise alors "de {receiver}" plutôt que la forme
                    # possessive, qui suppose que le prénom est déjà connu).
                    # Le contenu exact de l'intro dépend de la position (voir
                    # _restraint_intro), mais pas sa présence : on peut donc
                    # décider ici du gabarit d'action, hors boucle position.
                    has_intro = restraint != "libre" or blindfold
                    if has_intro:
                        action = f"{{actor}} {verb} {zone_possessive}{trailing}."
                    else:
                        action = f"{{actor}} {verb} {zone_article} de {{receiver}}{trailing}."
                    for position_const, position_title, position_clause in _CARESS_POSITIONS:
                        # Assis·e, les fesses reposent sur le siège : pas de
                        # caresse possible dessus dans cette position.
                        if zone_key == "fesses" and position_const == POSITION_ASSIS:
                            continue
                        intro = _restraint_intro(restraint, blindfold, position_const)
                        description = intro + action
                        if position_clause:
                            description += " " + position_clause
                        intensity = min(
                            5, base_intensity + int(restraint != "libre") + int(blindfold)
                        )
                        duration = min(
                            MAX_ACTIVITY_MINUTES,
                            base_duration + (1 if restraint != "libre" else 0),
                        )

                        accessory = _restraint_accessory(restraint)
                        if accessory is None and method_key == "objet":
                            accessory = _accessory_id("plume", required=False)

                        title_suffix = [
                            label
                            for label in (
                                _restraint_label(restraint, position_const),
                                "yeux bandés" if blindfold else None,
                                position_title,
                            )
                            if label
                        ]
                        title = f"{method_title} : {zone_title}"
                        if title_suffix:
                            title += " (" + ", ".join(title_suffix) + ")"

                        variants.append(
                            _activity(
                                f"caresse_{zone_key}_{method_key}_{restraint}_"
                                f"{'bandeau' if blindfold else 'sans'}_"
                                f"{position_const or 'aucune'}",
                                category,
                                PHASE_PRELIMINAIRES,
                                title,
                                description,
                                intensity,
                                duration=duration,
                                accessory=accessory,
                                practice=PRACTICE_LIENS if restraint != "libre" else None,
                                position=position_const,
                            )
                        )
    return variants


# ---------------------------------------------------------------------------
# Actes précis (oral, doigtage, stimulation manuelle/clitoridienne, jouet)
# déclinés selon la position de chacun des deux partenaires — par exemple
# une fellation avec l'un à genoux et l'autre assis ou debout, comme demandé
# explicitement. Contrairement aux caresses ci-dessus, ces actes distinguent
# la position de l'acteur ET celle du/de la receveur·se plutôt qu'une seule
# position partagée.
# ---------------------------------------------------------------------------

def _stance_text(position: str, e_placeholder: str) -> str:
    """Texte de posture pour une personne donnée : ``e_placeholder`` est le
    nom du placeholder d'accord féminin à utiliser pour CETTE personne
    (``{actor_e}`` ou ``{receiver_e}``), substitué plus tard côté
    sensor.py — jamais la notation "(e)"."""
    stances = {
        POSITION_ALLONGE: f"allongé{e_placeholder}",
        POSITION_QUATRE_PATTES: "à quatre pattes",
        POSITION_PENCHE_AVANT: (
            f"penché{e_placeholder} en avant, appuyé{e_placeholder} sur un meuble ou un mur"
        ),
        POSITION_DEBOUT: "debout",
        POSITION_ASSIS: f"assis{e_placeholder}, sur une chaise ou le bord du lit",
        POSITION_GENOUX: "à genoux",
    }
    return stances[position]


_POSITION_TITLES = {
    POSITION_ALLONGE: "allongé",
    POSITION_QUATRE_PATTES: "à quatre pattes",
    POSITION_PENCHE_AVANT: "penché",
    POSITION_DEBOUT: "debout",
    POSITION_ASSIS: "assis",
    POSITION_GENOUX: "à genoux",
}
_POSITIONS_LIST = [
    POSITION_ALLONGE,
    POSITION_QUATRE_PATTES,
    POSITION_PENCHE_AVANT,
    POSITION_DEBOUT,
    POSITION_ASSIS,
    POSITION_GENOUX,
]

# clé, catégorie, titre, gabarit (placeholders au premier degré : pas de
# .format() intermédiaire ici, donc pas d'accolades à doubler ; {actor} et
# {receiver} y sont chacun nommé·e une seule fois), sexe du/de la
# receveur·se, accessoire, pénétration ?, sexe oral ?
_POSITIONED_ACTS = [
    ("oral", CATEGORY_PRELIMINAIRES, "Stimulation orale",
     "{actor} fait {oral_on_receiver} à {receiver}.", SEX_INDIFFERENT, None, False, True),
    ("doigtage", CATEGORY_PRELIMINAIRES, "Doigtage",
     "{actor} caresse et pénètre {receiver} du bout des doigts.", SEX_FEMME, None, True, False),
    ("masturbation", CATEGORY_PRELIMINAIRES, "Stimulation manuelle",
     "{actor} stimule {receiver} avec la main.", SEX_HOMME, None, False, False),
    ("clitoridienne", CATEGORY_PRELIMINAIRES, "Stimulation clitoridienne",
     "{actor} stimule le clitoris de {receiver} du bout des doigts ou avec l'accessoire vibrant choisi.",
     SEX_FEMME, _accessory_category("vibrant", required=False), False, False),
    ("jouet", CATEGORY_PRELIMINAIRES, "Pénétration avec un jouet",
     "{actor} insère délicatement le jouet vibrant choisi et laisse {receiver} s'habituer à la sensation.",
     SEX_INDIFFERENT, _accessory_category("vibrant", required=True), True, False),
]


def _generate_positioned_acts() -> list[dict]:
    """Actes précis déclinés selon la position de chacun des deux
    partenaires ET selon la contrainte (libre, mains liées mais mobiles,
    attachées à un point fixe) — le couple a explicitement demandé de
    vérifier que chaque acte existe aussi bien attaché que libre. La
    position de {receiver} (celle dans laquelle iel reçoit l'acte) est
    enregistrée dans le champ ``position``, pour le questionnaire de
    postures ; celle de {actor} reste uniquement descriptive."""
    variants = []
    for act_key, category, act_title, template, receiver_sex, accessory, penetration, is_oral in _POSITIONED_ACTS:
        for actor_pos in _POSITIONS_LIST:
            for receiver_pos in _POSITIONS_LIST:
                # {actor} et {receiver} sont déjà chacun nommé·e une fois par
                # le gabarit de l'acte : la phrase de posture qui suit les
                # désigne donc par pronom (ou de nouveau par leur prénom pour
                # un couple de même sexe, voir _second_mention côté sensor).
                actor_stance = _stance_text(actor_pos, "{actor_e}")
                receiver_stance = _stance_text(receiver_pos, "{receiver_e}")
                stance_sentence = (
                    f" {{actor_ref_cap}} est {actor_stance}, {{receiver_ref}} est {receiver_stance}."
                )
                for restraint in _RESTRAINTS:
                    intro = _restraint_intro(restraint, blindfold=False, position=receiver_pos)
                    description = intro + template + stance_sentence
                    accessory_for_variant = accessory or _restraint_accessory(restraint)
                    practices = []
                    if restraint != "libre":
                        practices.append((PRACTICE_LIENS, "donne"))
                    if is_oral:
                        practices.append((PRACTICE_ORAL, "donne"))

                    title = f"{act_title} ({_POSITION_TITLES[actor_pos]} / {_POSITION_TITLES[receiver_pos]}"
                    if restraint != "libre":
                        title += ", " + _restraint_label(restraint, receiver_pos)
                    title += ")"

                    variants.append(
                        _activity(
                            f"acte_{act_key}_{actor_pos}_{receiver_pos}_{restraint}",
                            category,
                            PHASE_PRELIMINAIRES,
                            title,
                            description,
                            4,
                            duration=2,
                            accessory=accessory_for_variant,
                            practices=practices or None,
                            penetration=penetration,
                            receiver_sex=receiver_sex,
                            position=receiver_pos,
                        )
                    )
    return variants


# ---------------------------------------------------------------------------
# Intense, début de phase (voir intense_stage dans _activity() et
# DuoCoordinator._matches_intense_turn) : sexe oral et pénétration avec un
# jouet vibrant sur les 2 premiers tours, plus le doigtage intense
# limité au 1er tour et à une seule fois par receveur·se (voir
# ``once_per_phase`` et DuoCoordinator._matches_once_cap) — rien de tout
# cela n'est obligatoire, ce sont des options possibles, pas des passages
# forcés. Le reste de la phase Intense se limite aux positions nommées avec
# pénétration (voir _generate_kamasutra_positions). Déclinés selon la
# contrainte et le bandeau comme le reste du catalogue. Chaque acte a deux
# gabarits : ``template_no_intro`` nomme {receiver} lui-même (aucune intro
# liens/bandeau ne l'a fait avant), ``template_with_intro`` ne le/la
# re-nomme pas (déjà nommé·e par l'intro) — cette seconde version évite tout
# pronom objet direct/indirect pour rester correcte quel que soit le sexe
# (voir la mise en garde sur {actor_ref}/{receiver_ref} en objet).
#
# clé, catégorie, titre, gabarit sans intro, gabarit avec intro, sexe du/de
# la receveur·se, accessoire, pénétration ?, sexe oral ?, intense_stage,
# groupe once_per_phase (None si non plafonné, ex. le sexe oral est
# plafonné implicitement via son tag PRACTICE_ORAL — voir
# DuoCoordinator._once_per_phase_group).
# ---------------------------------------------------------------------------
_EARLY_INTENSE_ACTS = [
    (
        "oral", CATEGORY_INTENSITE_PLUS, "Stimulation orale intense",
        "{actor} fait {oral_on_receiver} à {receiver}, avec plus d'intensité et d'insistance qu'en préliminaires.",
        "{actor} passe à {oral_on_receiver}, avec plus d'intensité et d'insistance qu'en préliminaires.",
        SEX_INDIFFERENT, None, False, True, "early", None,
    ),
    (
        "doigtage", CATEGORY_INTENSITE_PLUS, "Doigtage intense",
        "{actor} pénètre {receiver} avec les doigts, avec un rythme plus soutenu et plus profond.",
        "{actor} intensifie la pénétration digitale, avec un rythme plus soutenu et plus profond.",
        SEX_FEMME, None, True, False, "first", "doigtage_intense",
    ),
    (
        "jouet", CATEGORY_INTENSITE_PLUS, "Pénétration avec un jouet vibrant",
        "{actor} pénètre {receiver} avec le jouet vibrant choisi (vibromasseur, godemichet...), en augmentant progressivement l'intensité.",
        "{actor} insère le jouet vibrant choisi (vibromasseur, godemichet...) et augmente progressivement l'intensité.",
        SEX_INDIFFERENT, _accessory_category("vibrant", required=True), True, False, "early", None,
    ),
]


def _generate_early_intense_acts() -> list[dict]:
    """Actes de début de phase Intense (sexe oral, doigtage, jouet vibrant),
    déclinés selon la contrainte et le bandeau — voir le commentaire
    au-dessus de _EARLY_INTENSE_ACTS."""
    variants = []
    for (
        act_key, category, act_title,
        template_no_intro, template_with_intro,
        receiver_sex, accessory, penetration, is_oral,
        intense_stage, once_per_phase,
    ) in _EARLY_INTENSE_ACTS:
        for restraint in _RESTRAINTS:
            for blindfold in (False, True):
                has_intro = restraint != "libre" or blindfold
                intro = _restraint_intro(restraint, blindfold)
                template = template_with_intro if has_intro else template_no_intro
                description = intro + template

                practices = []
                if restraint != "libre":
                    practices.append((PRACTICE_LIENS, "donne"))
                if is_oral:
                    practices.append((PRACTICE_ORAL, "donne"))
                if accessory is not None:
                    practices.append((PRACTICE_JOUETS, "usage"))

                intensity = min(5, 4 + int(restraint != "libre") + int(blindfold))
                duration = min(MAX_ACTIVITY_MINUTES, 2 + (1 if restraint != "libre" else 0))

                title_suffix = [
                    label
                    for label in (
                        _restraint_label(restraint, None),
                        "yeux bandés" if blindfold else None,
                    )
                    if label
                ]
                title = act_title
                if title_suffix:
                    title += " (" + ", ".join(title_suffix) + ")"

                variants.append(
                    _activity(
                        f"intense_early_{act_key}_{restraint}_"
                        f"{'bandeau' if blindfold else 'sans'}",
                        category,
                        PHASE_INTENSE,
                        title,
                        description,
                        intensity,
                        duration=duration,
                        accessory=accessory,
                        practices=practices or None,
                        penetration=penetration,
                        receiver_sex=receiver_sex,
                        intense_stage=intense_stage,
                        once_per_phase=once_per_phase,
                    )
                )
    return variants


# ---------------------------------------------------------------------------
# Fessée légère déclinée selon la position de {receiver} (celle dans laquelle
# iel la reçoit — voir le questionnaire de postures) et la contrainte. Reste
# autorisée en phase Intense, mais uniquement sur les 2 premiers tours
# (``intense_stage="early"``) et une seule fois par receveur·se sur toute la
# phase (``once_per_phase="fessee_intense"``, voir
# DuoCoordinator._matches_once_cap) — jamais obligatoire.
# ---------------------------------------------------------------------------

_FESSEE_ACTION = "{actor} donne une fessée légère à {receiver}, à l'intensité validée ensemble avant de commencer."


def _generate_fessee_variants() -> list[dict]:
    variants = []
    for position in _POSITIONS_LIST:
        # Assis·e, les fesses reposent sur le siège : pas de fessée possible
        # dans cette position (même raison que pour les caresses).
        if position == POSITION_ASSIS:
            continue
        for restraint in ("libre", "mobile"):
            intro = _restraint_intro(restraint, blindfold=False)
            stance = _stance_text(position, "{receiver_e}")
            description = f"{intro}{_FESSEE_ACTION} {{receiver_ref_cap}} est {stance}."

            practices = [(PRACTICE_DISCIPLINE, "donne")]
            if restraint != "libre":
                practices.append((PRACTICE_LIENS, "donne"))

            accessory = _restraint_accessory(restraint) or _accessory_id("fouet_leger", required=False)

            title = f"Fessée légère ({_POSITION_TITLES[position]}"
            if restraint != "libre":
                title += ", " + _RESTRAINT_LABELS[restraint]
            title += ")"

            variants.append(
                _activity(
                    f"fessee_{position}_{restraint}",
                    CATEGORY_INTENSITE_PLUS,
                    PHASE_INTENSE,
                    title,
                    description,
                    4,
                    duration=1,
                    accessory=accessory,
                    practices=practices,
                    position=position,
                    intense_stage="early",
                    once_per_phase="fessee_intense",
                )
            )
    return variants


# ---------------------------------------------------------------------------
# Intense, étape "late" (2 derniers tours) : positions nommées, réellement
# empruntées au Kama Sutra ou au tantra plutôt que des libellés génériques
# ("allongé", "à quatre pattes"...) — le couple a explicitement demandé leur
# vrai nom et une explication de leur fonctionnement (mise en place, pas de
# détail graphique). Le mélange volontaire d'``actor_sex``/``receiver_sex``
# fait que certaines positions placent la femme au-dessus, meneuse du rythme
# (Andromaque/Cavalière, Cow-girl inversée, Yab-Yum), d'autres la placent en
# dessous ou penchée (Missionnaire, Levrette, l'Ancre, la variante penchée
# sur un meuble) ; les Cuillères et la position debout contre un mur restent
# indifférentes au sexe. Comme pour le reste du catalogue, {receiver} n'est
# nommé·e qu'une fois : par l'intro liens/bandeau si elle existe (gabarit
# ``template_with_intro``, qui le/la redésigne alors par pronom quand le
# sexe est fixé par la position, ou l'omet quand il ne l'est pas), sinon par
# le gabarit ``template_no_intro`` lui-même. La position de {receiver} est
# enregistrée dans le champ ``position`` (voir le questionnaire de postures),
# celle de {actor} reste descriptive.
#
# clé, titre, gabarit sans intro, gabarit avec intro, sexe actor, sexe
# receiver, position de {receiver}.
# ---------------------------------------------------------------------------
_KAMASUTRA_POSITIONS = [
    (
        "missionnaire", "Missionnaire",
        "{actor} s'installe au-dessus de {receiver}, allongée sur le dos, jambes autour de lui — la position du Missionnaire, la plus classique, pour se regarder dans les yeux pendant la pénétration.",
        "{actor} s'installe au-dessus d'elle, jambes autour de lui — la position du Missionnaire, la plus classique, pour se regarder dans les yeux pendant la pénétration.",
        SEX_HOMME, SEX_FEMME, POSITION_ALLONGE,
    ),
    (
        "levrette", "Levrette",
        "{receiver} est à quatre pattes pendant que {actor} la pénètre par-derrière — la Levrette, appréciée pour la profondeur de pénétration qu'elle permet.",
        "toujours à quatre pattes, {actor} la pénètre par-derrière — la Levrette, appréciée pour la profondeur de pénétration qu'elle permet.",
        SEX_HOMME, SEX_FEMME, POSITION_QUATRE_PATTES,
    ),
    (
        "andromaque", "Andromaque (la Cavalière)",
        "{receiver} est allongé sur le dos pendant que {actor} s'installe au-dessus de lui et mène le rythme — la position d'Andromaque, aussi appelée la Cavalière, où la femme garde le contrôle du mouvement.",
        "toujours allongé sur le dos, {actor} s'installe au-dessus de lui et mène le rythme — la position d'Andromaque, aussi appelée la Cavalière, où la femme garde le contrôle du mouvement.",
        SEX_FEMME, SEX_HOMME, POSITION_ALLONGE,
    ),
    (
        "cowgirl_inversee", "Cow-girl inversée",
        "{receiver} est allongé sur le dos pendant que {actor} s'installe au-dessus de lui, dos tourné vers son visage — la Cow-girl inversée, une variante de la Cavalière qui change le point de vue et les sensations.",
        "toujours allongé sur le dos, {actor} s'installe au-dessus de lui, dos tourné vers son visage — la Cow-girl inversée, une variante de la Cavalière qui change le point de vue et les sensations.",
        SEX_FEMME, SEX_HOMME, POSITION_ALLONGE,
    ),
    (
        "yab_yum", "Yab-Yum",
        "{receiver} s'assoit, {actor} vient s'installer sur ses genoux, face à face, jambes entrelacées — le Yab-Yum, emprunté au tantra, pour un rapprochement maximal des corps et des regards.",
        "c'est {actor} qui vient s'installer sur ses genoux, face à face, jambes entrelacées — le Yab-Yum, emprunté au tantra, pour un rapprochement maximal des corps et des regards.",
        SEX_FEMME, SEX_HOMME, POSITION_ASSIS,
    ),
    (
        "cuilleres", "Cuillères",
        "{actor} et {receiver} s'allongent sur le côté, blottis l'un contre l'autre, pour une pénétration tout en douceur par-derrière — la position des Cuillères, intime et peu fatigante.",
        "{actor} vient se blottir dans son dos, allongé{actor_e} sur le côté, pour une pénétration tout en douceur par-derrière — la position des Cuillères, intime et peu fatigante.",
        SEX_INDIFFERENT, SEX_INDIFFERENT, POSITION_ALLONGE,
    ),
    (
        "debout_mur", "Debout contre un mur",
        "{actor} plaque doucement {receiver} contre un mur, debout, pour une pénétration face à face — une position qui demande un peu d'équilibre mais rapproche les corps.",
        "toujours contre le mur, {actor} entame une pénétration face à face — une position qui demande un peu d'équilibre mais rapproche les corps.",
        SEX_INDIFFERENT, SEX_INDIFFERENT, POSITION_DEBOUT,
    ),
    (
        "penche_meuble", "Penché·e sur un meuble",
        "{receiver} se penche en avant, appuyée sur un meuble ou le rebord du lit, pendant que {actor} la pénètre par-derrière — une variante de la Levrette, très prisée pour l'angle de pénétration qu'elle offre.",
        "toujours penchée en avant, appuyée sur un meuble, {actor} la pénètre par-derrière — une variante de la Levrette, très prisée pour l'angle de pénétration qu'elle offre.",
        SEX_HOMME, SEX_FEMME, POSITION_PENCHE_AVANT,
    ),
    (
        "ancre", "L'Ancre",
        "{receiver} est allongée sur le dos et lève les jambes sur les épaules de {actor}, agenouillé face à elle — la position de l'Ancre, qui permet une pénétration plus profonde.",
        "ses jambes reposent sur les épaules de {actor}, agenouillé face à elle — la position de l'Ancre, qui permet une pénétration plus profonde.",
        SEX_HOMME, SEX_FEMME, POSITION_ALLONGE,
    ),
]


def _generate_kamasutra_positions() -> list[dict]:
    """Positions nommées proposées aux 2 derniers tours de la phase Intense,
    déclinées selon la contrainte et le bandeau — voir le commentaire
    au-dessus de _KAMASUTRA_POSITIONS. Reprend le mécanisme de contrainte
    libre/mobile/fixe déjà utilisé ailleurs dans le catalogue (ex. Madame
    allongée sur le dos et attachée à un point fixe, les yeux bandés ou
    non, pour la position du Missionnaire ou de l'Ancre)."""
    variants = []
    for (
        position_key, title, template_no_intro, template_with_intro,
        actor_sex, receiver_sex, receiver_position,
    ) in _KAMASUTRA_POSITIONS:
        for restraint in _RESTRAINTS:
            for blindfold in (False, True):
                has_intro = restraint != "libre" or blindfold
                intro = _restraint_intro(restraint, blindfold, receiver_position)
                template = template_with_intro if has_intro else template_no_intro
                description = intro + template

                practices = []
                if restraint != "libre":
                    practices.append((PRACTICE_LIENS, "donne"))

                intensity = min(5, 4 + int(restraint != "libre") + int(blindfold))
                duration = min(MAX_ACTIVITY_MINUTES, 2 + (1 if restraint != "libre" else 0))

                title_suffix = [
                    label
                    for label in (
                        _restraint_label(restraint, receiver_position),
                        "yeux bandés" if blindfold else None,
                    )
                    if label
                ]
                variant_title = title
                if title_suffix:
                    variant_title += " (" + ", ".join(title_suffix) + ")"

                variants.append(
                    _activity(
                        f"intense_position_{position_key}_{restraint}_"
                        f"{'bandeau' if blindfold else 'sans'}",
                        CATEGORY_INTENSITE_PLUS,
                        PHASE_INTENSE,
                        variant_title,
                        description,
                        intensity,
                        duration=duration,
                        practices=practices or None,
                        penetration=True,
                        actor_sex=actor_sex,
                        receiver_sex=receiver_sex,
                        position=receiver_position,
                        intense_stage="late",
                    )
                )
    return variants


ACTIVITIES += (
    _generate_caress_variants()
    + _generate_positioned_acts()
    + _generate_early_intense_acts()
    + _generate_fessee_variants()
    + _generate_kamasutra_positions()
)


def get_activity(activity_id: str) -> dict | None:
    """Return the activity matching the given id, if any."""
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            return activity
    return None
