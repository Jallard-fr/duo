# Duo — Intimité de couple pour Home Assistant

Duo est une intégration [Home Assistant](https://www.home-assistant.io/) + une carte Lovelace dédiées aux couples adultes qui souhaitent pimenter leur vie intime, de façon ludique, textuelle et consentie.

> ⚠️ **Application réservée aux adultes (18 ans et plus).** L'installation demande une confirmation explicite de majorité et de consentement mutuel. Le contenu proposé reste volontairement **suggestif et non graphique** : Duo propose des thèmes et une ambiance, jamais des instructions explicites détaillées. Chaque partenaire peut refuser une suggestion à tout moment, sans justification.

## Fonctionnalités

- **Sexe de chaque partenaire** (homme/femme), renseigné à la configuration.
- **Actions paramétrées par sexe acteur/récepteur** : chaque activité du catalogue porte un champ `actor_sex` (sexe du partenaire qui agit) et `receiver_sex` (sexe du partenaire qui reçoit), valant `homme`, `femme` ou `indifferent`. Seules les activités compatibles avec le sexe des deux partenaires pour le tour en cours sont proposées.
- **Profil de préférences** par catégorie (préliminaires, sensoriel, massage, jeu de rôle, communication, intensité+), noté de 0 à 5 par chaque partenaire.
- **Humeur du soir** : chaque partenaire indique s'il/elle est partant(e), d'humeur douce, curieux(se), envie de nouveauté ou de torride, avec les accessoires qu'il/elle propose et une idée libre à tester. L'autre partenaire est notifié en push sur tous ses appareils mobiles.
- **Association partenaire ↔ personne Home Assistant** (facultative) : chacun ne peut alors modifier que sa propre humeur, et Duo sait à qui envoyer la notification.
- **Suggestions à tour de rôle**, pondérées selon les préférences, l'humeur, le sexe acteur/récepteur et les accessoires disponibles.
- **Chronomètre** intégré, avec une durée aléatoire dans la plage définie pour chaque activité (ou personnalisable).
- **Mémoire du couple** : les activités déclinées sont mises "en pause" (14 jours par défaut) et ne sont proposées à nouveau automatiquement que si le partenaire concerné choisit explicitement l'humeur "Envie de nouveauté".
- **Gestion des accessoires** disponibles au sein du couple, utilisés pour filtrer les suggestions compatibles — modifiable depuis la carte ou directement depuis les options de l'intégration.
- **Réinitialisation automatique à minuit** des humeurs du soir.
- **Historique** des dernières sessions (activité, réponse, tour).

## Architecture du dépôt

```
custom_components/duo/
  __init__.py            Point d'entrée, services, enregistrement automatique de la carte
  config_flow.py         Assistant de configuration (prénoms, sexe, consentement, personne HA)
  coordinator.py         État runtime, mémoire persistante, minuteur, notifications
  activities.py          Catalogue des suggestions (texte, non graphique, sexe acteur/récepteur)
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
3. Vérifiez que l'URL `/duo_frontend/duo-card.js?v=<version>` (le numéro de version doit correspondre à celui du journal) répond bien avec du code JavaScript et non une erreur.

## Services disponibles

| Service | Description |
|---|---|
| `duo.set_preference` | Enregistre la note (0-5) d'un partenaire pour une catégorie |
| `duo.set_accessories` | Met à jour la liste des accessoires du couple |
| `duo.set_mood` | Met à jour l'humeur du soir d'un partenaire (accessoires, idée libre) et notifie l'autre |
| `duo.request_suggestion` | Propose une nouvelle activité (tour optionnel), filtrée par sexe acteur/récepteur |
| `duo.respond_suggestion` | Accepte ou décline la suggestion en cours |
| `duo.start_timer` | (Re)démarre le minuteur, durée personnalisable |
| `duo.stop_timer` | Arrête le minuteur |
| `duo.reset_session` | Réinitialise la suggestion/minuteur en cours |
| `duo.clear_profile` | Réinitialise entièrement le profil du couple |

## Philosophie du contenu

Toutes les suggestions du catalogue (`custom_components/duo/activities.py`) sont écrites à un niveau **suggestif, catégoriel et non graphique**. Duo ne décrit jamais d'acte sexuel explicite : il propose une ambiance, une durée, un thème et un ciblage acteur/récepteur, et laisse le couple libre de décider, ensemble et dans le respect de leurs limites, comment vivre le moment.

## Licence

Usage personnel. Adaptez librement ce dépôt à vos besoins.
