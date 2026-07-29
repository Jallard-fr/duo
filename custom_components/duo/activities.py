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
        "preliminaires_cuir_chevelu", CATEGORY_MASSAGE, PHASE_PRELIMINAIRES,
        "Caresses dans les cheveux",
        "{actor} caresse et masse doucement le cuir chevelu de {receiver}, en jouant avec ses cheveux.",
        1, count=(20, "caresses"),
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

    # ------------------------------------------------------------------
    # Phase 3 — Intense : actions avec pénétration intense.
    # ------------------------------------------------------------------
    _activity(
        "intense_carte_blanche", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Carte blanche",
        "{actor} prend l'initiative avec {receiver} et fait monter la température, dans le respect des limites fixées dans leur profil.",
        5, duration=3,
    ),
    _activity(
        "intense_nouveaute", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Nouveauté assumée",
        "{actor} et {receiver} retentent, à deux, quelque chose qu'ils avaient décliné auparavant — uniquement s'ils en ont tous les deux réellement envie ce soir.",
        4, duration=3,
    ),
    _activity(
        "intense_negociation", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "À négocier ensemble",
        "{actor} et {receiver} discutent ensemble de quelque chose de nouveau à essayer ce soir, et se mettent d'accord avant de se lancer.",
        4, duration=2,
    ),
    _activity(
        "intense_rythme", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Défi de rythme",
        "{actor} et {receiver} alternent qui mène le rythme du moment, en changeant à chaque sonnerie du minuteur.",
        5, duration=3,
    ),
    _activity(
        "intense_accessoire_vibrant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Accessoire à deux",
        "{actor} et {receiver} intègrent ensemble l'accessoire vibrant qu'ils possèdent, au rythme et à l'intensité qui leur conviennent.",
        5, duration=3,
        accessory=_accessory_category("vibrant", required=False),
        practice=PRACTICE_JOUETS,
    ),
    _activity(
        "intense_rythme_lent", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Ralenti assumé",
        "{actor} et {receiver} ralentissent consciemment chaque geste, sans chercher à accélérer.",
        3, duration=3,
    ),
    _activity(
        "intense_instant_rapide", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Instant bref",
        "{actor} et {receiver} s'accordent un moment bref et intense, sans préambule, pour changer du rythme habituel.",
        5, duration=1,
    ),
    _activity(
        "intense_discipline_legere", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Fessée légère",
        "{actor} donne une fessée légère à {receiver}, à la main ou avec l'accessoire choisi, à l'intensité validée ensemble avant de commencer.",
        4, duration=1,
        accessory=_accessory_id("fouet_leger", required=False),
        practice=PRACTICE_DISCIPLINE,
    ),
    _activity(
        "intense_liens_du_soir", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Liens du soir",
        "{actor} utilise des liens doux pour immobiliser gentiment {receiver}, avec un mot d'arrêt clair et respecté par les deux.",
        4, duration=2,
        accessory=_accessory_id("menottes_douces", required=False),
        practice=PRACTICE_LIENS,
    ),
    _activity(
        "intense_gel_chauffant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Chaleur qui monte",
        "{actor} applique le gel chauffant choisi sur {receiver} et laisse la sensation s'installer avant de continuer.",
        3, duration=1,
        accessory=_accessory_id("gel_chauffant", required=False),
    ),
    _activity(
        "intense_confort_lubrifiant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Confort avant tout",
        "{actor} et {receiver} prennent un instant pour appliquer du lubrifiant si besoin : le confort d'abord.",
        1, duration=1,
        accessory=_accessory_id("lubrifiant", required=False),
    ),
    _activity(
        "intense_protection", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Protection avant tout",
        "{actor} et {receiver} prennent un instant, ensemble, pour la protection si besoin.",
        1, duration=1,
        accessory=_accessory_id("preservatifs", required=False),
        actor_sex=SEX_HOMME,
    ),
    _activity(
        "intense_position_allonge", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : allongé",
        "{actor} et {receiver} s'installent allongés, comme ils le sentent sur le moment.",
        4, duration=1, position=POSITION_ALLONGE,
    ),
    _activity(
        "intense_position_quatre_pattes", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : à quatre pattes",
        "{actor} et {receiver} passent à la position à quatre pattes, à leur rythme.",
        4, duration=1, position=POSITION_QUATRE_PATTES,
    ),
    _activity(
        "intense_position_penche_avant", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : penché en avant",
        "{actor} et {receiver} essaient la position penchés en avant, appuyés sur le lit ou un meuble stable.",
        4, duration=1, position=POSITION_PENCHE_AVANT,
    ),
    _activity(
        "intense_position_debout", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : debout",
        "{actor} et {receiver} passent à une position debout, contre un support stable.",
        4, duration=1, position=POSITION_DEBOUT,
    ),
    _activity(
        "intense_position_assis", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : assis",
        "{actor} et {receiver} essaient une position assise, sur une chaise ou le bord du lit.",
        4, duration=1, position=POSITION_ASSIS,
    ),
    _activity(
        "intense_position_genoux", CATEGORY_INTENSITE_PLUS, PHASE_INTENSE,
        "Position : à genoux",
        "{actor} et {receiver} passent à une position à genoux, au sol ou sur le lit.",
        4, duration=1, position=POSITION_GENOUX,
    ),

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
    ("cuir_chevelu", "le cuir chevelu", "son cuir chevelu", "Cuir chevelu"),
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
# plus tôt dans la description à ce stade : on utilise {receiver_ref} (un
# pronom pour un couple hétérosexuel, sinon le prénom répété) plutôt que de
# le/la renommer une deuxième fois, et {receiver_e} pour accorder l'adjectif
# au féminin le cas échéant (plutôt que la notation "(e)").
_CARESS_POSITIONS = [
    (None, None, None),
    (POSITION_ALLONGE, "allongé", "{receiver_ref} est allongé{receiver_e}."),
    (POSITION_QUATRE_PATTES, "à quatre pattes", "{receiver_ref} est à quatre pattes."),
    (
        POSITION_PENCHE_AVANT,
        "penché",
        "{receiver_ref} est penché{receiver_e} en avant, appuyé{receiver_e} sur un meuble ou un mur.",
    ),
    (POSITION_DEBOUT, "debout", "{receiver_ref} est debout."),
    (
        POSITION_ASSIS,
        "assis",
        "{receiver_ref} est assis{receiver_e}, sur une chaise ou le bord du lit.",
    ),
    (POSITION_GENOUX, "à genoux", "{receiver_ref} est à genoux."),
]


def _restraint_intro(restraint: str, blindfold: bool) -> str:
    """Phrase d'introduction posant le contexte (liens, bandeau) avant
    l'action elle-même ; vide si ni l'un ni l'autre ne s'applique. Nomme
    {receiver} une seule fois : c'est toujours la première mention de la
    description quand elle est présente."""
    if restraint == "mobile":
        extra = " et les yeux bandés" if blindfold else ""
        return "{receiver} a les mains liées mais mobiles" + extra + ", pendant que "
    if restraint == "fixe":
        extra = ", les yeux bandés," if blindfold else ""
        return "{receiver} est attaché{receiver_e} à un point fixe" + extra + " pendant que "
    if blindfold:
        return "Les yeux bandés, {receiver} se laisse surprendre pendant que "
    return ""


def _restraint_accessory(restraint: str) -> dict | None:
    if restraint == "mobile":
        return _accessory_id("foulards", required=True)
    if restraint == "fixe":
        return _accessory_id("menottes_douces", required=True)
    return None


def _generate_caress_variants() -> list[dict]:
    variants = []
    for zone_key, zone_article, zone_possessive, zone_title in _CARESS_ZONES:
        for method_key, category, method_title, verb, trailing, base_intensity, base_duration in _CARESS_METHODS:
            for restraint in _RESTRAINTS:
                for blindfold in (False, True):
                    intro = _restraint_intro(restraint, blindfold)
                    # {receiver} n'est nommé·e qu'une fois : par l'intro
                    # ci-dessus si elle existe, sinon par l'action elle-même
                    # (qui utilise alors "de {receiver}" plutôt que la forme
                    # possessive, qui suppose que le prénom est déjà connu).
                    if intro:
                        action = f"{{actor}} {verb} {zone_possessive}{trailing}."
                    else:
                        action = f"{{actor}} {verb} {zone_article} de {{receiver}}{trailing}."
                    for position_const, position_title, position_clause in _CARESS_POSITIONS:
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
                                _RESTRAINT_LABELS[restraint],
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
                    f" {{actor_ref}} est {actor_stance}, {{receiver_ref}} est {receiver_stance}."
                )
                for restraint in _RESTRAINTS:
                    intro = _restraint_intro(restraint, blindfold=False)
                    description = intro + template + stance_sentence
                    accessory_for_variant = accessory or _restraint_accessory(restraint)
                    practices = []
                    if restraint != "libre":
                        practices.append((PRACTICE_LIENS, "donne"))
                    if is_oral:
                        practices.append((PRACTICE_ORAL, "donne"))

                    title = f"{act_title} ({_POSITION_TITLES[actor_pos]} / {_POSITION_TITLES[receiver_pos]}"
                    if restraint != "libre":
                        title += ", " + _RESTRAINT_LABELS[restraint]
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
# Fessée légère déclinée selon la position de {receiver} (celle dans laquelle
# iel la reçoit — voir le questionnaire de postures) et la contrainte, comme
# demandé explicitement (ex. une fessée à quatre pattes).
# ---------------------------------------------------------------------------

_FESSEE_ACTION = "{actor} donne une fessée légère à {receiver}, à l'intensité validée ensemble avant de commencer."


def _generate_fessee_variants() -> list[dict]:
    variants = []
    for position in _POSITIONS_LIST:
        for restraint in ("libre", "mobile"):
            intro = _restraint_intro(restraint, blindfold=False)
            stance = _stance_text(position, "{receiver_e}")
            description = f"{intro}{_FESSEE_ACTION} {{receiver_ref}} est {stance}."

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
                )
            )
    return variants


ACTIVITIES += (
    _generate_caress_variants()
    + _generate_positioned_acts()
    + _generate_fessee_variants()
)


def get_activity(activity_id: str) -> dict | None:
    """Return the activity matching the given id, if any."""
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            return activity
    return None
