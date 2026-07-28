# Duo — Intimité de couple pour Home Assistant

Duo est une intégration [Home Assistant](https://www.home-assistant.io/) + une carte Lovelace dédiées aux couples adultes qui souhaitent pimenter leur vie intime, de façon ludique, textuelle et consentie.

> ⚠️ **Application réservée aux adultes (18 ans et plus).** L'installation demande une confirmation explicite de majorité et de consentement mutuel. Le contenu proposé reste volontairement **suggestif et non graphique** : Duo propose des thèmes et une ambiance, jamais des instructions explicites détaillées. Chaque partenaire peut refuser une suggestion à tout moment, sans justification. **La santé passe avant tout** : le catalogue exclut délibérément toute pratique présentant un risque physique réel — l'application sert uniquement le plaisir, jamais au détriment de la sécurité.

## Fonctionnalités

- **Sexe de chaque partenaire** (homme/femme), renseigné à la configuration.
- **Actions paramétrées par sexe acteur/récepteur** : chaque activité du catalogue porte un champ `actor_sex` (sexe du partenaire qui agit) et `receiver_sex` (sexe du partenaire qui reçoit), valant `homme`, `femme` ou `indifferent`. Seules les activités compatibles avec le sexe des deux partenaires pour le tour en cours sont proposées.
- **Profil de préférences** par catégorie (préliminaires, sensoriel, massage, jeu de rôle, communication, intensité+, tendresse & après), noté de 0 à 5 par chaque partenaire. **0 = catégorie exclue** (plus jamais proposée), sauf si le partenaire active le mode "braver ses interdits" (voir plus bas).
- **Deux questionnaires fermés**, accessibles depuis la carte (section "Préférences & accessoires"), rejouables à tout moment :
  - **Questionnaire de préférences** : une question par catégorie ("Jamais / Parfois / Souvent / Toujours").
  - **Questionnaire de limites** : des questions explicites, groupées par pratique — stimulation orale, pénétration anale, discipline légère, contrainte douce/liens, jouets vibrants — chacune posée séparément pour le rôle actif ("acceptes-tu de faire...") et le rôle passif ("acceptes-tu de recevoir..."), avec 3 réponses possibles (Oui / À voir / Non). Un "non" exclut l'activité correspondante du catalogue pour ce rôle (ex. la sodomie peut être exclue par l'un des deux sans affecter l'autre). Le libellé s'adapte au sexe concerné (fellation/cunnilingus).
  - **Chaque questionnaire est verrouillé à une seule personne** : si l'identité (via association à une personne Home Assistant) est connue, il démarre directement pour cette personne ; sinon un écran "qui répond ?" est affiché avant la première question, pour qu'on ne réponde jamais par erreur à la place de l'autre.
- **Braver ses interdits** : un bouton personnel par partenaire qui, une fois activé, rend à nouveau proposables les catégories/pratiques qu'il a exclues et les activités récemment déclinées, pour les prochaines suggestions — jusqu'à ce qu'il le désactive.
- **Permissions par partenaire** : si une personne Home Assistant est associée à chaque partenaire, préférences, limites et mode "braver ses interdits" ne sont modifiables que par la personne concernée — comme c'était déjà le cas pour l'humeur du soir.
- **Humeur du soir** : chaque partenaire indique s'il/elle est partant(e), d'humeur douce, curieux(se), envie de nouveauté ou de torride, avec les accessoires qu'il/elle propose et une idée libre à tester. L'autre partenaire est notifié en push sur tous ses appareils mobiles.
- **Association partenaire ↔ personne Home Assistant** (facultative) : chacun ne peut alors modifier que sa propre humeur, et Duo sait à qui envoyer la notification.
- **Suggestions à tour de rôle**, pondérées selon les préférences, l'humeur, le sexe acteur/récepteur, la phase visée et les accessoires disponibles.
- **Phases temporelles du rapport** : chaque activité est rattachée à un moment — **Excitation** (encore habillés, début de la stimulation), **Préliminaires** (contacts avec les zones érogènes : baisers, caresses des doigts ou de la bouche), **Intense** (pénétration intense) ou **Résolution** (tendresse après) — inspirées du modèle des phases de la réponse sexuelle de Masters & Johnson (1966) et du modèle triphasique de Kaplan (1979), adaptées à un usage concret pour le couple. On peut demander une suggestion pour une phase précise (service ou carte) plutôt que de piocher au hasard dans tout le catalogue.
- **Chronomètre** intégré, avec une durée fixe (non aléatoire) propre à chaque activité, pour que le couple sache toujours à quoi s'attendre avant d'accepter — avec des bips sonores dans la carte (toutes les 30 s, puis un bip différent chaque seconde dans les 10 dernières secondes) — désactivables via le bouton 🔊/🔇 de la carte.
- **Activités courtes** : chaque activité dure au maximum 3 minutes (souvent moins), ou est quantifiée en un nombre fixe d'actions plutôt qu'en temps (ex. "10 baisers", "20 mouvements de massage") — pour enchaîner sans que rien ne s'éternise et casser la routine.
- **Personnalisation par prénom** : les descriptions d'activité utilisent directement les prénoms configurés du couple (ex. "Alice caresse Bob...") plutôt qu'une formule générique comme "votre partenaire". Les mots techniques "acteur"/"récepteur" ne sont eux jamais affichés dans la carte — ils restent un vocabulaire interne au filtrage par sexe.
- **Accessoire intégré au titre** : quand une activité est associée à un accessoire (requis ou simplement conseillé), son nom apparaît directement dans le titre affiché (ex. "Massage à l'huile (avec Huile de massage)") plutôt que dans une ligne séparée.
- **Positions génériques** : certaines activités de la phase Intense proposent une mise en scène (allongé, à quatre pattes, debout, assis, à genoux...), comme simple élément de variété, jamais associée à une description d'acte.
- **Progression guidée par niveau (= phase)** : chaque partenaire doit faire accepter 3 activités de la phase en cours avant de passer automatiquement à la suivante (Excitation → Préliminaires → Intense → Résolution). En cas de refus, jusqu'à 4 nouvelles propositions sont faites automatiquement avant de laisser la main au couple.
- **Mémoire du couple** : les activités déclinées sont mises "en pause" (14 jours par défaut) et ne sont proposées à nouveau automatiquement que si le partenaire concerné choisit explicitement l'humeur "Envie de nouveauté".
- **Catalogue prédéfini d'accessoires** (fichier unique `accessories.py`), classé par catégories (sensoriel, jeux de couple, vibrant, contrainte douce, lingerie, soins) : chaque partenaire coche simplement ce qu'il possède déjà, depuis la carte ou les options de l'intégration — plus besoin de saisir quoi que ce soit à la main. Chaque activité indique si son accessoire est **requis** (l'activité n'est proposée que si le couple le possède) ou simplement **conseillé** (l'activité reste possible sans, juste moins souvent proposée).
- **Accessoires paramétrés par sexe acteur/récepteur**, sur le même principe que les activités : par ex. la lingerie fine est rattachée à un acteur femme (peu importe le récepteur), un anneau vibrant ou un préservatif à un acteur homme, et les jouets vibrants pensés pour une stimulation féminine à un récepteur femme. Un accessoire incompatible avec le sexe acteur/récepteur du tour en cours est traité comme indisponible pour ce tour.
- **Réinitialisation automatique à minuit** des humeurs du soir.
- **Historique** des dernières sessions (activité, réponse, tour).

## Architecture du dépôt

```
custom_components/duo/
  __init__.py            Point d'entrée, services, enregistrement automatique de la carte
  config_flow.py         Assistant de configuration (prénoms, sexe, consentement, personne HA)
  coordinator.py         État runtime, mémoire persistante, minuteur, notifications
  activities.py          Catalogue des suggestions (53 activités, texte non graphique, durée ≤ 3 min ou comptage, position, sexe acteur/récepteur)
  accessories.py         Catalogue prédéfini d'accessoires (seule source ; lu dynamiquement par la carte)
  sensor.py / select.py  Entités exposées (suggestion, minuteur, humeur, historique, soirée)
  services.yaml          Définition des services appelables
  frontend/duo-card.js   Carte Lovelace (servie automatiquement par l'intégration)

hacs.json                Métadonnées pour une installation via HACS
```

## Installation

### Option A — via HACS (recommandé)

1. Dans Home Assistant : **HACS → Intégrations (⋮) → Dépôts personnalisés**.
2. Ajoutez l'URL de ce dépôt GitHub, catégorie **Intégration**.
3. Installez **"Duo - Intimité de couple"**, puis redémarrez Home Assistant.

La carte Lovelace est servie automatiquement par l'intégration (`/duo_frontend/duo-card.js`) : aucune ressource à ajouter manuellement dans la plupart des cas.

### Option B — installation manuelle

1. Copiez le dossier `custom_components/duo` dans `<config>/custom_components/duo`.
2. Redémarrez Home Assistant.
3. Si la ressource Lovelace n'apparaît pas automatiquement (mode YAML notamment), ajoutez-la vous-même : **Paramètres → Tableaux de bord → ⋮ → Ressources → Ajouter une ressource**
   - URL : `/duo_frontend/duo-card.js`
   - Type : Module JavaScript

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration → Duo**.
2. Renseignez le prénom et le sexe (homme/femme) de chaque partenaire, associez éventuellement chacun à une **personne Home Assistant** (`person.*`), puis confirmez la case de majorité/consentement mutuel (obligatoire).
3. Dans les **options** de l'intégration (Paramètres → Appareils et services → Duo → Configurer), vous pouvez à tout moment ajuster l'association personne/notify, surcharger manuellement les services `notify.*` utilisés, et **modifier la liste des accessoires du couple** (séparés par des virgules) — sans passer par la carte.
4. Notez l'`entry_id` généré si besoin (visible via **Outils de développement → Modèles** avec `{{ config_entries()|selectattr('domain','eq','duo')|map(attribute='entry_id')|list }}`).

## Ajouter la carte au tableau de bord

Le plus simple : ajoutez une carte, choisissez **"Duo - Intimité de couple"** dans la liste, et laissez l'éditeur visuel pré-remplir les entités détectées.

En YAML :

```yaml
type: custom:duo-card
entry_id: "VOTRE_ENTRY_ID"
partner1: "Alice"
partner2: "Bob"
suggestion_entity: sensor.duo_alice_bob_current_suggestion
timer_entity: sensor.duo_alice_bob_timer
evening_entity: sensor.duo_alice_bob_soiree
history_entity: sensor.duo_alice_bob_historique
mood_entity_partner1: select.duo_mood_alice
mood_entity_partner2: select.duo_mood_bob
```

Adaptez les `entity_id` aux noms réellement générés par votre installation (visibles dans **Outils de développement → États**, filtrez sur `duo`).

### Thème de la carte

Un sélecteur en haut de la carte permet à chaque personne qui consulte le tableau de bord de choisir son propre thème visuel (Home Assistant, Romantique, Nuit, Élégant, Doux) : le choix est mémorisé dans le navigateur, indépendamment du thème global du tableau de bord. Un thème par défaut peut aussi être fixé via le champ `theme` de la configuration de la carte (éditeur visuel ou YAML), par ex. `theme: sombre`.

### La carte ne s'affiche pas ("Custom element doesn't exist: duo-card")

L'enregistrement de la carte est entièrement automatique : rien à ajouter à la main dans le cas normal. Si ça coince malgré tout :

1. L'enregistrement est maintenant tenté à la fois au chargement du composant et à chaque chargement de l'entrée Duo, ce qui le rend plus fiable qu'avant. En cas d'échec réel, une **notification persistante** apparaît directement dans l'interface Home Assistant (cloche en haut à droite) avec le détail de l'erreur — inutile donc de fouiller les journaux pour le savoir.
2. Si aucune notification n'apparaît et que la carte ne s'affiche toujours pas après un redémarrage complet, fermez entièrement l'onglet/l'application (pas seulement un rechargement) et rouvrez le tableau de bord : certains onglets déjà ouverts ou installations en PWA ne relisent la liste des scripts qu'à une navigation complète, pas à une simple reconnexion.
3. En dernier recours, vérifiez dans **Paramètres → Système → Journal** (filtrez sur `duo`) la présence de la ligne `Duo : carte servie sur /duo_frontend/duo-card.js?v=...`.
4. Vérifiez que l'URL `/duo_frontend/duo-card.js?v=<version>` (le numéro de version doit correspondre à celui du journal) répond bien avec du code JavaScript et non une erreur.

## Services disponibles

| Service | Description |
|---|---|
| `duo.set_preference` | Enregistre la note (0-5) d'un partenaire pour une catégorie |
| `duo.set_accessories` | Met à jour la liste des accessoires du couple |
| `duo.set_brave_taboos` | Active/désactive, pour un partenaire, le fait de braver ses catégories exclues et ses activités récemment déclinées |
| `duo.set_practice_limit` | Enregistre la réponse (oui/à voir/non) d'un partenaire à une question du questionnaire de limites |
| `duo.set_mood` | Met à jour l'humeur du soir d'un partenaire (accessoires, idée libre) et notifie l'autre |
| `duo.request_suggestion` | Propose une nouvelle activité (tour et phase optionnels), filtrée par sexe acteur/récepteur et accessoires disponibles |
| `duo.respond_suggestion` | Accepte ou décline la suggestion en cours |
| `duo.start_timer` | (Re)démarre le minuteur, durée personnalisable |
| `duo.stop_timer` | Arrête le minuteur |
| `duo.reset_session` | Réinitialise la suggestion/minuteur en cours |
| `duo.clear_profile` | Réinitialise entièrement le profil du couple |

## Philosophie du contenu

Toutes les suggestions du catalogue (`custom_components/duo/activities.py`, 53 entrées) sont écrites à un niveau **suggestif, catégoriel et non graphique**. Duo ne décrit jamais d'acte sexuel explicite : il propose une ambiance, une durée (3 minutes maximum, imposée par le code) ou un nombre d'actions, un thème, un ciblage acteur/récepteur, une phase et parfois une position générique, et laisse le couple libre de décider, ensemble et dans le respect de leurs limites, comment vivre le moment. Aucune activité n'est inspirée d'une pratique présentant un risque physique réel (étouffement, bâillonnement...) — la santé prime toujours sur la nouveauté.

Le découpage en phases (`custom_components/duo/const.py`, `PHASE_*`) s'inspire de deux modèles de référence en sexologie — le modèle des phases de la réponse sexuelle de **Masters & Johnson** (*Human Sexual Response*, 1966) et le modèle triphasique de **Helen Singer Kaplan** (1979), qui a mis en avant la phase de désir en amont — adaptés à un découpage pratique en 4 étapes concrètes :

1. **Excitation** — encore habillés, début de la stimulation (par ex. un partenaire va mettre une tenue sexy).
2. **Préliminaires** — contacts avec les zones érogènes : baisers, caresses des doigts ou de la bouche (une pénétration digitale relève encore de cette phase).
3. **Intense** — actions avec pénétration intense (par ex. l'usage d'un accessoire vibrant à deux).
4. **Résolution** — retour au calme, tendresse après le rapport.

## Licence

Usage personnel. Adaptez librement ce dépôt à vos besoins.
