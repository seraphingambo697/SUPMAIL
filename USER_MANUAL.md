# SUPMEAL — Manuel utilisateur

Bienvenue sur **SUPMEAL**, votre outil de gestion de recettes et de planification de repas.

---

## 1. Créer un compte et se connecter

Deux façons de vous connecter, depuis la page **Connexion** :

1. **Compte classique** : cliquez sur "S'inscrire", renseignez un nom d'utilisateur, un e-mail et un mot de passe.
2. **Via un fournisseur externe** : cliquez sur "Continuer avec Google / GitHub / Microsoft". Vous êtes redirigé vers le fournisseur, autorisez l'accès, et vous êtes automatiquement connecté (un compte SUPMEAL est créé lors de la première connexion).

---

## 2. Tableau de bord

À la connexion, vous arrivez sur votre tableau de bord qui résume :
- vos **cookbooks** récents,
- vos **recettes favorites**,
- vos **recettes ajoutées récemment**.

---

## 3. Gérer vos recettes

### Créer une recette
1. Menu **Recettes** → **+ Nouvelle recette**.
2. Renseignez le titre, le temps de préparation/cuisson, le nombre de portions.
3. Ajoutez les ingrédients un par un (nom, quantité, unité).
4. Rédigez les étapes (une instruction par ligne).
5. Ajoutez des tags (cuisine, régime, difficulté), une image et une source (URL ou "création personnelle").
6. Choisissez si la recette est **personnelle** ou destinée à un **cookbook partagé**.
7. Cliquez sur **Créer la recette**.

### Consulter / modifier une recette
Cliquez sur une recette pour voir le détail : ingrédients, étapes, temps, portions. Si vous en avez le droit (propriétaire, ou éditeur/créateur du cookbook), les boutons **Modifier** et **Supprimer** sont disponibles.

### Marquer en favori
Sur la fiche recette, cliquez sur **☆ Ajouter aux favoris**.

---

## 4. Filtrer et rechercher

Dans le menu **Recettes**, une barre de filtres vous permet de combiner :
- recherche plein texte (titre, étapes, ingrédients, tags),
- cookbook d'origine (ou "mes recettes seules"),
- tag,
- ingrédient précis,
- temps de préparation/cuisson maximum,
- favoris uniquement.

---

## 5. Cookbooks partagés

### Créer un cookbook
Menu **Cookbooks** → **+ Nouveau cookbook**, renseignez un nom et une description. Vous en devenez automatiquement le **créateur**.

### Inviter des membres
Ouvrez votre cookbook → onglet **Membres** → renseignez l'e-mail de la personne à inviter et choisissez son rôle :
- **Éditeur** : peut ajouter/modifier des recettes et inviter d'autres membres.
- **Commentateur** : peut commenter les recettes mais pas les modifier.
- **Lecteur** : peut uniquement consulter.

Si la personne possède déjà un compte SUPMEAL, elle est ajoutée immédiatement. Sinon, l'invitation apparaîtra dans son onglet **Cookbooks** dès qu'elle créera un compte avec cet e-mail.

### Gérer les rôles
Le créateur peut changer le rôle d'un membre ou le retirer depuis l'onglet **Membres**.

### Rechercher dans un cookbook
Chaque cookbook a sa propre barre de recherche (onglet **Recettes** du cookbook) : recherche par titre, ingrédients, tags ou contenu des étapes.

### Discuter avec les membres
Onglet **Messagerie** : envoyez des messages visibles par tous les membres du cookbook. Les nouveaux messages apparaissent automatiquement toutes les quelques secondes.

### Commenter une recette
Sur la fiche d'une recette appartenant à un cookbook, une zone de commentaires est disponible en bas de page (visible si vous avez au moins le rôle Commentateur).

---

## 6. Planification de repas

Menu **Planning** :
1. Choisissez une recette, une date et un type de repas (petit-déjeuner, déjeuner, dîner, collation).
2. Cliquez sur **Ajouter au planning** : la recette apparaît dans la semaine correspondante.
3. Naviguez entre les semaines avec les flèches.
4. Cliquez sur **Générer pour cette semaine** pour obtenir automatiquement une **liste de courses agrégée** (quantités additionnées sur l'ensemble des recettes planifiées, ajustées au nombre de portions prévu).

---

## 7. Import / Export

Menu **Import / Export** :

- **Exporter** : choisissez le format (JSON compatible Mealie, ou CSV) et téléchargez l'ensemble de vos recettes et cookbooks. ⚠️ Le fichier contient vos données en clair — conservez-le en lieu sûr.
- **Importer** : sélectionnez un fichier JSON ou CSV exporté depuis SUPMEAL (ou compatible Mealie) et cliquez sur **Importer**. Vous devenez automatiquement le créateur des recettes/cookbooks importés.

---

## 8. Paramètres

Menu **Paramètres** :
- Modifiez votre prénom/nom.
- Renseignez vos **préférences culinaires** : régime alimentaire, allergies, cuisine préférée, nombre de portions par défaut — utile pour préremplir vos futures recettes et affiner les filtres.
- Changez votre mot de passe (indisponible si vous vous êtes connecté via OAuth2, puisque vous n'avez pas de mot de passe SUPMEAL).

---

## 9. Bon à savoir

- Toutes vos actions (création, modification, suppression) sont soumises aux permissions définies par votre rôle dans chaque cookbook.
- Les recettes personnelles (non rattachées à un cookbook) ne sont visibles que par vous.
- Vous pouvez à tout moment quitter SUPMEAL en exportant vos données (section 7).
