# Duo — Intimité de couple pour Home Assistant

Duo est une intégration [Home Assistant](https://www.home-assistant.io/) + une carte Lovelace dédiées aux couples adultes qui souhaitent pimenter leur vie intime, de façon ludique, textuelle et consentie.

> ⚠️ **Application réservée aux adultes (18 ans et plus).** L'installation demande une confirmation explicite de majorité et de consentement mutuel. Le contenu proposé reste volontairement **suggestif et non graphique** : Duo propose des thèmes et une ambiance, jamais des instructions explicites détaillées. Chaque partenaire peut refuser une suggestion à tout moment, sans justification.

## Fonctionnalités

- **Profil de préférences** par catégorie (préliminaires, sensoriel, massage, jeu de rôle, communication, intensité+), noté de 0 à 5 par chaque partenaire.
- **Humeur du soir** : chaque partenaire indique s'il/elle est partant(e), d'humeur douce, curieux(se), envie de nouveauté ou de torride.
- **Suggestions à tour de rôle**, pondérées selon les préférences, l'humeur et les accessoires disponibles.
- **Chronomètre** intégré, avec une durée aléatoire dans la plage définie pour chaque activité (ou personnalisable).
- **Mémoire du couple** : les activités déclinées sont mises "en pause" (14 jours par défaut) et ne sont proposées à nouveau automatiquement que si le partenaire concerné choisit explicitement l'humeur "Envie de nouveauté".
- **Gestion des accessoires** disponibles au sein du couple, utilisés pour filtrer les suggestions compatibles.
- **Historique** des dernières sessions (activité, réponse, tour).

## Architecture du dépôt

```
custom_components/duo/       Intégration Home Assistant (backend)
  __init__.py                 Point d'entrée, enregistrement des services
  config_flow.py              Assistant de configuration (prénoms + consentement)
  coordinator.py               État runtime, mémoire persistante, minuteur
  activities.py                 Catalogue des suggestions (texte, non graphique)
  sensor.py / select.py         Entités exposées (suggestion, minuteur, humeur, historique)
  services.yaml                 Définition des services appelables

www/duo-card/duo-card.js     Carte Lovelace (frontend, JS pur, sans build)
hacs.json                    Métadonnées pour une installation via HACS
```

## Installation

### Option A — via HACS (recommandé)

1. Dans Home Assistant : **HACS → Intégrations (⋮) → Dépôts personnalisés**.
2. Ajoutez l'URL de ce dépôt GitHub, catégorie **Intégration**.
3. Installez **"Duo - Intimité de couple"**, puis redémarrez Home Assistant.
4. Ajoutez ensuite la carte : **HACS → Frontend (⋮) → Dépôts personnalisés**, ajoutez ce même dépôt en catégorie **Lovelace**, puis installez la carte "Duo - Intimité de couple".

### Option B — installation manuelle

1. Copiez le dossier `custom_components/duo` dans `<config>/custom_components/duo`.
2. Copiez `www/duo-card/duo-card.js` dans `<config>/www/duo-card/duo-card.js`.
3. Redémarrez Home Assistant.
4. Ajoutez la ressource Lovelace : **Paramètres → Tableaux de bord → ⋮ → Ressources → Ajouter une ressource**
   - URL : `/local/duo-card/duo-card.js`
   - Type : Module JavaScript

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration → Duo**.
2. Renseignez le prénom de chaque partenaire et confirmez la case de majorité/consentement mutuel (obligatoire).
3. Notez l'`entry_id` généré (visible dans l'URL de la page de configuration de l'intégration, ou via **Outils de développement → Modèles** avec `{{ config_entries()|selectattr('domain','eq','duo')|map(attribute='entry_id')|list }}`).

## Ajouter la carte au tableau de bord

Exemple de configuration YAML de carte :

```yaml
type: custom:duo-card
entry_id: "VOTRE_ENTRY_ID"
partner1: "Alice"
partner2: "Bob"
suggestion_entity: sensor.duo_alice_bob_current_suggestion
timer_entity: sensor.duo_alice_bob_timer
history_entity: sensor.duo_alice_bob_history
mood_entity_partner1: select.duo_mood_alice
mood_entity_partner2: select.duo_mood_bob
```

Adaptez les `entity_id` aux noms réellement générés par votre installation (visibles dans **Outils de développement → États**, filtrez sur `duo`).

## Services disponibles

| Service | Description |
|---|---|
| `duo.set_preference` | Enregistre la note (0-5) d'un partenaire pour une catégorie |
| `duo.set_accessories` | Met à jour la liste des accessoires du couple |
| `duo.set_mood` | Met à jour l'humeur du soir d'un partenaire |
| `duo.request_suggestion` | Propose une nouvelle activité (tour optionnel) |
| `duo.respond_suggestion` | Accepte ou décline la suggestion en cours |
| `duo.start_timer` | (Re)démarre le minuteur, durée personnalisable |
| `duo.stop_timer` | Arrête le minuteur |
| `duo.reset_session` | Réinitialise la suggestion/minuteur en cours |
| `duo.clear_profile` | Réinitialise entièrement le profil du couple |

## Philosophie du contenu

Toutes les suggestions du catalogue (`custom_components/duo/activities.py`) sont écrites à un niveau **suggestif, catégoriel et non graphique**. Duo ne décrit jamais d'acte sexuel explicite : il propose une ambiance, une durée et un thème, et laisse le couple libre de décider, ensemble et dans le respect de leurs limites, comment vivre le moment.

## Licence

Usage personnel. Adaptez librement ce dépôt à vos besoins.
