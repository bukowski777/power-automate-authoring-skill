# Power Automate depuis VS Code, Codex ou Claude Code

Date: 2026-05-18

Ce guide décrit une méthode générique pour créer, modifier, versionner et déployer des cloud flows Power Automate depuis un environnement local, VS Code, Codex ou Claude Code.

Il ne dépend pas d'un tenant particulier. Les noms d'environnement, de solution, de site SharePoint, de comptes et de listes doivent être remplacés par les valeurs du projet cible.

## Quand utiliser cette méthode

Utiliser cette méthode quand:

- un flow doit être modifié proprement avec revue de diff;
- plusieurs expressions Power Automate doivent être corrigées;
- un flow doit être durci avec une structure `TRY` / `CATCH`;
- un changement doit être reproductible entre environnements;
- VS Code, Codex ou Claude Code doit manipuler la définition JSON du flow.

Éviter de créer un flow complexe entièrement à la main en JSON. Pour un flow neuf, le plus fiable reste de créer un squelette dans le portail Power Automate, puis de l'exporter dans une solution pour le compléter localement.

## Vue d'ensemble

Workflow recommandé:

1. Créer ou vérifier une solution Power Platform dédiée.
2. Créer le squelette du flow dans le portail si le flow est neuf.
3. Exporter la solution avec Power Platform CLI (`pac`).
4. Dépaqueter la solution localement.
5. Modifier les workflows JSON dans VS Code, Codex ou Claude Code.
6. Valider les JSON et les expressions sensibles.
7. Repaqueter la solution.
8. Importer dans l'environnement cible.
9. Publier les personnalisations.
10. Réexporter pour vérifier la définition réellement stockée.
11. Tester un run réel et un cas d'erreur.

## Pré-requis

Outils locaux recommandés:

- Power Platform CLI: `pac`;
- Microsoft 365 CLI: `m365`;
- Node.js et `npm`, idéalement via `nvm`;
- `jq` pour inspecter les JSON;
- `rg` pour chercher vite dans les exports;
- Git;
- VS Code, Codex ou Claude Code.

Vérifier les outils:

```bash
node --version
npm --version
pac help
m365 version
jq --version
rg --version
git status
```

Installer Microsoft 365 CLI si besoin:

```bash
npm install -g @pnp/cli-microsoft365
```

Sur macOS avec `nvm`:

```bash
source "$HOME/.nvm/nvm.sh"
nvm use <node-version>
npm install -g @pnp/cli-microsoft365
```

## Authentification

Se connecter à Microsoft 365:

```bash
m365 login
m365 status --output json
```

Se connecter à Power Platform:

```bash
pac auth create --environment <environment-url-or-id>
pac auth list
```

Sélectionner un profil existant:

```bash
pac auth select --index <profile-index>
```

Contrôler que la solution cible existe:

```bash
pac solution list
```

## Paramètres projet à définir

Chaque projet doit définir ses valeurs, dans un README projet, `.env.local`, variables de shell ou documentation interne:

```bash
export PA_ENVIRONMENT_URL="<dataverse-environment-url>"
export PA_SOLUTION_NAME="<solution-name>"
export PA_WORK_DIR="tmp/power-automate/<change-name>"
export PA_SITE_URL="<sharepoint-site-url>"
export PA_LIST_TITLE="<sharepoint-list-title>"
```

Exemple générique:

```bash
export PA_SOLUTION_NAME="MySolution"
export PA_WORK_DIR="tmp/power-automate/add-error-logging"
```

Ne pas versionner les zips de solution, exports temporaires, tokens ou secrets.

## Préparer le dossier de travail

```bash
mkdir -p "$PA_WORK_DIR"
```

Convention utile:

```text
tmp/power-automate/<change-name>/
  before.zip
  unpacked/
  after.zip
  verify.zip
  verify/
```

## Exporter la solution

Toujours partir de l'état réel Dataverse:

```bash
pac solution export \
  --name "$PA_SOLUTION_NAME" \
  --path "$PA_WORK_DIR/before.zip" \
  --managed false \
  --overwrite
```

Dépaqueter:

```bash
rm -rf "$PA_WORK_DIR/unpacked"
pac solution unpack \
  --zipfile "$PA_WORK_DIR/before.zip" \
  --folder "$PA_WORK_DIR/unpacked" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber
```

Lister les workflows:

```bash
find "$PA_WORK_DIR/unpacked/Workflows" -maxdepth 1 -name '*.json' -print
```

Inspecter les actions principales:

```bash
for f in "$PA_WORK_DIR"/unpacked/Workflows/*.json; do
  echo "== ${f##*/}"
  jq -r '.properties.definition.actions | to_entries[] | "  \(.key): \(.value.type)"' "$f" | sed -n '1,20p'
done
```

## Modifier un flow existant

Ouvrir le fichier JSON du flow dans:

```text
<work-dir>/unpacked/Workflows/
```

Bonnes pratiques:

- préserver les `connectionName`, `operationId`, `apiId` et connection references existantes;
- modifier uniquement le flow concerné;
- nommer les actions de façon stable et lisible;
- garder une structure `runAfter` explicite;
- relire tous les chemins de succès, échec, timeout et annulation;
- éviter les refactors massifs non nécessaires;
- vérifier les flows proches qui réutilisent les mêmes expressions.

Valider le JSON:

```bash
jq empty "$PA_WORK_DIR/unpacked/Workflows/<workflow-file>.json"
```

Inspecter une action:

```bash
jq '.properties.definition.actions.<ActionName>' \
  "$PA_WORK_DIR/unpacked/Workflows/<workflow-file>.json"
```

Chercher une expression:

```bash
rg -n "formatNumber|float|TRY_|CATCH_|runAfter|<field-name>" "$PA_WORK_DIR/unpacked/Workflows"
```

## Créer un nouveau flow

Méthode recommandée:

1. Dans Power Automate, créer le flow dans la solution cible.
2. Choisir le déclencheur dans le portail.
3. Ajouter les connecteurs et actions qui créent les connection references.
4. Sauvegarder le flow.
5. Exporter la solution avec `pac`.
6. Compléter ou factoriser la logique dans le JSON local.

Pourquoi cette approche:

- les triggers Power Automate ont une structure JSON spécifique;
- les connecteurs créent des références de connexion difficiles à deviner;
- les actions AI Builder, SharePoint, Outlook, Dataverse ou SQL ont souvent des paramètres internes non évidents;
- le portail garantit que le squelette est valide avant édition locale.

Créer un workflow par copie d'un fichier JSON existant est possible, mais plus risqué. Il faut alors maîtriser les IDs, dépendances, références de connexion, noms logiques et composants de solution.

## Pattern TRY/CATCH

Pour les flows de production, encapsuler la logique métier dans un scope `TRY`.

Pattern:

- `TRY_<domain>`: actions métier;
- `CATCH_<domain>`: s'exécute si `TRY_<domain>` échoue ou timeoute;
- `result('TRY_<domain>')`: récupère les résultats des actions du scope;
- filtrer les actions dont le statut n'est pas `Succeeded`;
- créer un résumé lisible;
- envoyer une alerte ou écrire un log.

Bloc minimal à placer dans `CATCH_<domain>` pour récupérer les logs du scope `TRY_<domain>`:

```json
"Compose_catch_try_result": {
  "type": "Compose",
  "inputs": "@result('TRY_<domain>')"
},
"Filter_catch_failed_actions": {
  "type": "Query",
  "inputs": {
    "from": "@outputs('Compose_catch_try_result')",
    "where": "@or(equals(item()?['status'], 'Failed'), equals(item()?['status'], 'TimedOut'))"
  },
  "runAfter": {
    "Compose_catch_try_result": [
      "Succeeded"
    ]
  }
},
"Select_catch_error_details": {
  "type": "Select",
  "inputs": {
    "from": "@body('Filter_catch_failed_actions')",
    "select": {
      "action": "@item()?['name']",
      "status": "@item()?['status']",
      "code": "@coalesce(item()?['error']?['code'], item()?['code'], item()?['outputs']?['statusCode'], '')",
      "message": "@coalesce(item()?['error']?['message'], item()?['outputs']?['body']?['error']?['message'], item()?['outputs']?['body']?['message'], '')",
      "startTime": "@item()?['startTime']",
      "endTime": "@item()?['endTime']",
      "trackingId": "@coalesce(item()?['trackingId'], item()?['clientTrackingId'], '')"
    }
  },
  "runAfter": {
    "Filter_catch_failed_actions": [
      "Succeeded"
    ]
  }
},
"Compose_catch_log_payload": {
  "type": "Compose",
  "inputs": {
    "flowName": "@coalesce(workflow()?['tags']?['flowDisplayName'], workflow()?['name'])",
    "environment": "@coalesce(workflow()?['tags']?['environmentName'], '')",
    "runName": "@workflow()?['run']?['name']",
    "runId": "@workflow()?['run']?['id']",
    "loggedAtUtc": "@utcNow()",
    "businessKey": "@variables('varLogBusinessKey')",
    "sourceItemId": "@variables('varLogSourceItemId')",
    "sourceFileName": "@variables('varLogSourceFileName')",
    "failedActions": "@body('Select_catch_error_details')",
    "rawTryResult": "@outputs('Compose_catch_try_result')"
  },
  "runAfter": {
    "Select_catch_error_details": [
      "Succeeded"
    ]
  }
}
```

Les variables `varLogBusinessKey`, `varLogSourceItemId` et `varLogSourceFileName` doivent être initialisées avant `TRY_<domain>`, pour que le `CATCH` ne dépende pas d'une action potentiellement échouée.

Le `runAfter` du scope `CATCH_<domain>` doit généralement être:

```json
"runAfter": {
  "TRY_<domain>": [
    "Failed",
    "TimedOut"
  ]
}
```

Ajouter `Skipped` uniquement si un scope `TRY` ignoré doit déclencher une alerte.

Le log doit contenir autant que possible:

- nom du flow;
- environnement;
- run ID;
- contexte métier;
- item, fichier ou entité concernée;
- action en erreur;
- statut;
- code HTTP si disponible;
- code erreur si disponible;
- message;
- heures de début/fin;
- tracking ID si disponible;
- extrait brut de `result('TRY_<domain>')`.

Destinataire:

- utiliser une adresse de support définie par le projet;
- ne pas coder une adresse personnelle dans un guide générique;
- documenter le destinataire dans les paramètres projet.

## Expressions Power Automate

Points à surveiller:

- `int()` échoue facilement si la valeur est un flottant ou une chaîne mal normalisée;
- pour des centimes, préférer `formatNumber(mul(<amount>, 100), '0')`;
- normaliser les montants avant `float()` si l'OCR renvoie devise, espaces ou virgule décimale;
- protéger les champs facultatifs avec `coalesce()` et `empty()`;
- attention aux dates `AM/PM`: ne pas forcer `formatDateTime()` si la chaîne n'est pas ISO 8601;
- éviter de mélanger texte OCR brut et champs structurés sans contrôle.

Exemple de normalisation de montant:

```text
replace(
  replace(
    replace(
      replace(trim(string(<amount-text>)), '€', ''),
      'EUR',
      ''
    ),
    ' ',
    ''
  ),
  ',',
  '.'
)
```

## Packer la solution

```bash
pac solution pack \
  --zipfile "$PA_WORK_DIR/after.zip" \
  --folder "$PA_WORK_DIR/unpacked" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber
```

Si `SolutionPackager` signale des composants racine non définis, vérifier si l'avertissement existait déjà dans les exports précédents. Ne pas l'ignorer si le composant est nouveau ou lié à la modification.

## Importer et publier

```bash
pac solution import \
  --path "$PA_WORK_DIR/after.zip" \
  --publish-changes \
  --force-overwrite
```

Points à vérifier:

- import terminé sans erreur;
- personnalisations publiées;
- le flow est encore activé si l'environnement l'exige;
- les références de connexion sont toujours résolues;
- aucun composant hors périmètre n'a été modifié.

## Réexporter pour contrôle

Réexporter après import:

```bash
pac solution export \
  --name "$PA_SOLUTION_NAME" \
  --path "$PA_WORK_DIR/verify.zip" \
  --managed false \
  --overwrite

rm -rf "$PA_WORK_DIR/verify"
pac solution unpack \
  --zipfile "$PA_WORK_DIR/verify.zip" \
  --folder "$PA_WORK_DIR/verify" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber
```

Vérifier que l'action ou expression attendue est bien présente:

```bash
rg -n "TRY_|CATCH_|<action-name>|<expression-fragment>" "$PA_WORK_DIR/verify/Workflows"
```

## Lire ou contrôler SharePoint depuis un agent local

Avec Microsoft 365 CLI:

```bash
m365 request \
  --method get \
  --url "$PA_SITE_URL/_api/web/lists/getbytitle('$PA_LIST_TITLE')/items?\$top=5" \
  --output json | jq
```

Pour des titres avec espaces, encoder l'URL ou utiliser une variable déjà encodée selon le shell.

## Tests de validation

Tests minimum après import:

- déclencheur: vérifier qu'un run part;
- chemin nominal: vérifier le résultat attendu;
- chemin d'erreur: provoquer une erreur contrôlée et vérifier le log;
- non-régression: rejouer un cas connu;
- données: contrôler les champs écrits dans SharePoint, Dataverse ou la cible;
- doublons: tester un renvoi ou une modification répétée si le flow crée des items;
- permissions: vérifier que le compte de connexion peut lire/écrire toutes les ressources.

## Travail avec Codex ou Claude Code

Bon mode opératoire:

1. Demander à l'agent d'exporter la solution actuelle.
2. Demander une inspection ciblée du flow.
3. Faire modifier uniquement les actions nécessaires.
4. Exiger une validation `jq`.
5. Exiger un pack/import.
6. Exiger un réexport de contrôle.
7. Exiger un résumé des risques et tests restants.

Consignes utiles:

- ne pas modifier un flow hors périmètre;
- ne pas versionner les zips;
- ne pas écrire de secrets dans les docs;
- documenter tout pattern réutilisable;
- committer seulement les fichiers source/doc versionnés.

Points spécifiques à Claude Code:

- placer les règles projet dans `CLAUDE.md` si l'équipe utilise Claude Code comme agent principal;
- si le dépôt utilise déjà `AGENTS.md`, dupliquer ou référencer les consignes critiques dans `CLAUDE.md` pour éviter deux sources divergentes;
- donner explicitement le périmètre: solution, environnement, flows autorisés, flows interdits;
- demander à Claude Code de travailler depuis un export frais, jamais depuis un vieux zip;
- demander une liste des fichiers modifiés et des commandes exécutées;
- demander un réexport de contrôle après import, comme avec Codex.

Commandes qu'un agent local peut utiliser sans modifier le tenant:

```bash
pac auth list
pac solution list
pac solution export --name "$PA_SOLUTION_NAME" --path "$PA_WORK_DIR/before.zip" --managed false --overwrite
pac solution unpack --zipfile "$PA_WORK_DIR/before.zip" --folder "$PA_WORK_DIR/unpacked" --packagetype Unmanaged --allowWrite --clobber
jq empty "$PA_WORK_DIR/unpacked/Workflows/<workflow-file>.json"
rg -n "TRY_|CATCH_|runAfter" "$PA_WORK_DIR/unpacked/Workflows"
git diff --check
```

Commandes à considérer comme impactantes:

```bash
pac solution import --path "$PA_WORK_DIR/after.zip" --publish-changes --force-overwrite
pac solution publish
m365 flow enable
m365 flow disable
m365 flow remove
```

Pour ces commandes, l'agent doit annoncer précisément l'impact attendu et vérifier ensuite l'état réel.

## Travail avec VS Code

Extensions utiles:

- JSON language support intégré;
- GitLens ou équivalent pour la revue;
- Power Platform Tools si utilisé dans l'équipe;
- REST Client si des appels SharePoint/Graph sont testés.

Réglages pratiques:

- formater le JSON seulement si toute l'équipe accepte le bruit de diff;
- utiliser `jq` pour extraire les sous-arbres plutôt que lire tout le fichier;
- garder un export de référence avant modification.

## Documentation projet

Chaque projet devrait compléter ce guide par une courte fiche locale:

```text
Solution Power Platform:
Environnement:
Compte de connexion:
Site SharePoint:
Listes/bibliothèques:
Destinataire logs:
Dossier local temporaire:
Flows critiques:
Tests obligatoires:
```

Cette fiche locale peut contenir les noms tenant/projet, alors que ce guide reste générique.

## Limites connues

- `m365 flow` peut être limité par les consentements Entra du tenant.
- Les commandes `m365 request` peuvent fonctionner même si les commandes `m365 flow` sont bloquées.
- Un JSON valide ne garantit pas que les expressions Power Automate seront valides au runtime.
- Certains imports remplacent une définition et peuvent désactiver ou demander une réactivation de flow.
- Les connecteurs premium, gateway SQL et AI Builder doivent être testés dans l'environnement cible.
- Un flow très modifié dans le portail entre l'export et l'import peut être écrasé par le zip local.
