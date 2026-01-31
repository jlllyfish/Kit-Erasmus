# Moose - Gestion des mobilités Moow EFP

Interface Flask pour gérer l'envoi de conventions vers Démarches Simplifiées.

## 📍 Emplacements des éléments visuels

### LOGO
- **Fichier**: `app/static/logo.png`
- **Position**: En haut à gauche du header
- **Code**: `app/templates/base.html` ligne ~15
- **CSS**: `.logo` dans `app/static/css/style.css` ligne ~37

### TITRE ET SOUS-TITRE
- **Position**: Header, à droite du logo
- **Code**: `app/templates/base.html` lignes ~18-22
- **CSS**: `.main-title` et `.subtitle` dans `app/static/css/style.css` lignes ~43-54

### ICÔNES DES BLOCS STATS
- **Type**: SVG inline
- **Position**: En haut de chaque bloc statistique
- **Code**: `app/templates/dashboard.html` lignes ~9, ~22, ~35
- **CSS**: `.stat-icon` dans `app/static/css/style.css` ligne ~123
- **Modification**: Remplacer le code SVG directement dans le template

#### Bloc 1 - Total (icône document)
```html
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" ...>
```

#### Bloc 2 - À signer (icône clipboard)
```html
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" ...>
```

#### Bloc 3 - Envoyées (icône check)
```html
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" ...>
```

### BOUTON ENVOI
- **Position**: Centre de la page, entre les stats et les logs
- **Code**: `app/templates/dashboard.html` ligne ~54
- **CSS**: `.send-button` dans `app/static/css/style.css` ligne ~152

## 🎨 Personnalisation visuelle

### Couleurs
Toutes les couleurs sont dans `app/static/css/style.css`:
- Fond blanc: `#ffffff`
- Blocs/boutons noirs: `#000000`
- Texte blanc: `#ffffff`

### Design
- Blocs arrondis: `border-radius: 20px`
- Bouton gélule: `border-radius: 50px`
- Ombres: `box-shadow`

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer .env
cp .env.example .env
# Éditer .env avec vos vraies valeurs

# Ajouter votre logo
# Placer votre fichier logo.png dans app/static/

# Lancer l'application
python run.py
```

## 📂 Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── routes.py              # Routes et logique
│   ├── services/
│   │   ├── grist_service.py   # API Grist
│   │   ├── dn_service.py      # Upload DN
│   │   └── upload_service.py  # Script principal
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # 📍 TOUS LES STYLES ICI
│   │   ├── js/
│   │   │   └── main.js        # Interactions JS
│   │   └── logo.png           # 📍 LOGO ICI
│   └── templates/
│       ├── base.html          # 📍 HEADER + NAV
│       └── dashboard.html     # 📍 BLOCS + BOUTON + LOGS
├── config.py
├── run.py
└── requirements.txt
```

## 🔧 Fonctionnalités

- **Dashboard Kit E+**: Affiche les stats en temps réel
- **Envoi automatique**: Bouton pour lancer l'envoi des conventions
- **Logs en direct**: Suivi des opérations d'envoi
- **Rafraîchissement auto**: Les stats se mettent à jour après envoi