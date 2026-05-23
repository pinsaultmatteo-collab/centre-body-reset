# Centre Body Reset — Site internet

Site multi-pages du Centre Body Reset à Clermont-l'Hérault.
Conçu par PMC Marketing.

## 📁 Structure

```
centrebodyreset-v2/
├── index.html                # Page d'accueil
├── robots.txt
├── sitemap.xml
├── vercel.json
├── css/
│   └── main.css              # CSS global partagé
├── js/
│   └── layout.js             # Header + Footer + interactions globales
├── images/                   # Photos et logos
└── pages/
    ├── a-propos.html
    ├── tarifs.html
    ├── contact.html
    ├── blog.html             # Liste des articles
    ├── mentions-legales.html
    ├── confidentialite.html
    ├── cgv.html
    ├── solutions/            # 6 pages problématiques
    │   ├── silhouette.html
    │   ├── menopause.html
    │   ├── sommeil.html
    │   ├── sportifs.html
    │   ├── bien-etre-urinaire.html
    │   └── drainage.html
    ├── technologies/         # 5 pages technologies
    │   ├── cryolipolyse.html
    │   ├── adipologie.html
    │   ├── led.html
    │   ├── pressotherapie.html
    │   └── chaise-ems.html
    └── blog/                 # Articles
        ├── menopause-prise-de-poids.html
        ├── sommeil-recuperation.html
        └── chaise-ems-quest-ce-que-c-est.html
```

## ⚙️ Système d'includes

Le header et le footer sont injectés via JavaScript depuis `js/layout.js`.
Chaque page contient simplement :

```html
<div id="site-header"></div>
... contenu spécifique ...
<div id="site-footer"></div>
<script src="../js/layout.js"></script>
```

**Avantage** : modifier le menu ou le footer dans un seul fichier (`js/layout.js`)
et toutes les 19 pages se mettent à jour automatiquement.

## 🎨 Design system

Les variables CSS sont définies dans `css/main.css` (couleurs, typographies, espacements).
Pour modifier la palette, c'est là qu'il faut intervenir.

**Couleurs principales :**
- Cream : `#FAF7F2`
- Terracotta : `#C4704A`
- Sage : `#6B8C5A`
- Brun foncé : `#2A201B`

**Typographies :**
- Titres : Cormorant Garamond
- Corps : DM Sans

## 📝 Modifier les pages

- **Modifier le menu/footer** → `js/layout.js`
- **Modifier les styles globaux** → `css/main.css`
- **Modifier les couleurs** → variables `:root` dans `css/main.css`
- **Modifier le contenu d'une page** → fichier `.html` correspondant

## 📨 Formulaire de contact

Le formulaire de contact (`pages/contact.html`) affiche actuellement
une simple confirmation. Pour qu'il envoie réellement les messages,
brancher un service comme **Formspree** ou **Netlify Forms** :

```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
```

## 🚀 Déploiement

Le site est déployé sur Vercel : https://centre-body-reset.vercel.app
