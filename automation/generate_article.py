#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération automatique d'un article de blog SEO pour le Centre Body Reset.
Appelle l'API Claude pour rédiger un article complet, génère le fichier HTML
à partir du template, met à jour blog.html et sitemap.xml.

Lancé chaque mardi 8h par GitHub Actions.
"""

import os
import sys
import json
import html
import re
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

import anthropic

# ─────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent  # racine du repo
BLOG_DIR = ROOT / "pages" / "blog"
BLOG_INDEX = ROOT / "pages" / "blog.html"
SITEMAP = ROOT / "sitemap.xml"
CALENDRIER = ROOT / "automation" / "calendrier-editorial.json"
IMAGES_DIR = ROOT / "images" / "blog"  # dossier des images d'articles

SITE_URL = "https://www.centrebodyreset.fr"
MODELE = "claude-sonnet-4-6"  # modèle utilisé pour la rédaction

# Image de secours si le téléchargement Pexels échoue (photo déjà présente sur le site)
IMAGE_FALLBACK = "tech-led.webp"

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]


# ─────────────────────────────────────────────────────────
# 1. CHOIX DU SUJET
# ─────────────────────────────────────────────────────────
def charger_calendrier():
    with open(CALENDRIER, "r", encoding="utf-8") as f:
        return json.load(f)


def choisir_sujet(calendrier):
    """Retourne le premier sujet 'a_publier', ou None si tout est publié."""
    for sujet in calendrier["sujets"]:
        if sujet.get("statut") == "a_publier":
            return sujet
    return None


def marquer_publie(calendrier, sujet_id):
    for sujet in calendrier["sujets"]:
        if sujet["id"] == sujet_id:
            sujet["statut"] = "publie"
            sujet["date_publication"] = datetime.now().strftime("%Y-%m-%d")
    with open(CALENDRIER, "w", encoding="utf-8") as f:
        json.dump(calendrier, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────
# 2. GÉNÉRATION DU CONTENU VIA CLAUDE
# ─────────────────────────────────────────────────────────
def generer_article(client, sujet):
    """Appelle l'API Claude et renvoie un dict avec le contenu structuré."""

    prompt = f"""Tu es la plume éditoriale du Centre Body Reset, un centre de bien-être et santé globale à Clermont-l'Hérault, cofondé par Charlotte (diététicienne-nutritionniste diplômée depuis 2009, co-gérante) et Alison (esthéticienne et experte en technologies avancées depuis 2012, co-gérante).

Le centre propose : cryolipolyse, adipologie (technologie LFU® par ultrasons), photobiomodulation LED, pressodynamie (drainage par machine Starvac), et chaise EMS (renforcement du plancher pelvien). Approche : combiner technologies validées et expertise nutritionnelle, sans survente, avec honnêteté et pédagogie.

Rédige un article de blog optimisé SEO sur le sujet suivant :
- Titre indicatif : {sujet['titre_indicatif']}
- Catégorie : {sujet['categorie']}
- Mots-clés à intégrer naturellement : {', '.join(sujet['mots_cles'])}
- Angle éditorial : {sujet['angle']}
- Auteur : {sujet['auteur']}

CONSIGNES DE RÉDACTION :
- Ton : expert, bienveillant, honnête. Jamais survendeur. On informe avant de vendre.
- Longueur : 900 à 1200 mots.
- Public : grand public français, principalement des femmes 35-65 ans.
- Structure : 4 à 6 sections H2, avec quelques H3 si pertinent.
- Intègre les mots-clés naturellement (pas de bourrage).
- Termine toujours par une section "En résumé".
- Évite les promesses médicales exagérées. Reste factuel.

CONSIGNES DE FORMAT (réponds UNIQUEMENT en JSON valide, sans texte autour, sans backticks) :
{{
  "titre": "Le titre final de l'article (peut différer du titre indicatif, accrocheur, < 70 caractères)",
  "titre_html": "Le titre avec UN segment de 2-4 mots entouré de <em> pour le mettre en valeur en terracotta",
  "meta_description": "Meta description SEO, 150-160 caractères, avec mot-clé principal",
  "chapeau": "Phrase d'introduction en italique sous le titre (le 'lead'), 2-3 phrases accrocheuses",
  "temps_lecture": "X min de lecture (estime selon la longueur, ex: '7 min de lecture')",
  "corps_html": "Le corps COMPLET de l'article en HTML. Utilise UNIQUEMENT ces balises : <p>, <h2>, <h3>, <ul>/<li>, <strong>, <em>, <blockquote>. Pour les liens internes vers les pages du centre, utilise ces chemins relatifs EXACTS quand c'est pertinent : technologies <a href=\\"../technologies/cryolipolyse.html\\">, <a href=\\"../technologies/adipologie.html\\">, <a href=\\"../technologies/led.html\\">, <a href=\\"../technologies/pressotherapie.html\\">, <a href=\\"../technologies/chaise-ems.html\\"> ; solutions <a href=\\"../solutions/menopause.html\\">, <a href=\\"../solutions/sommeil.html\\">, <a href=\\"../solutions/sportifs.html\\">, <a href=\\"../solutions/silhouette.html\\">. Insère 2 à 4 liens internes pertinents. Inclus UN <blockquote> avec une citation forte. Inclus si pertinent UN encart au format : <div class=\\"callout\\"><strong>Titre encart</strong><p>Contenu</p></div>. NE PAS inclure de section CTA ni de 'En résumé' dans le corps : ils sont gérés séparément. Termine le corps juste avant la conclusion.",
  "resume_html": "Le contenu de la section 'En résumé' : 2 paragraphes <p> qui synthétisent l'article."
}}

Réponds en JSON pur, rien d'autre."""

    print(f"  → Appel API Claude (modèle {MODELE})...")
    message = client.messages.create(
        model=MODELE,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Nettoyage : enlever d'éventuels backticks markdown
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  ✗ Erreur parsing JSON : {e}")
        print(f"  Réponse brute :\n{raw[:500]}")
        raise

    return data


# ─────────────────────────────────────────────────────────
# 2bis. TÉLÉCHARGEMENT DE L'IMAGE (Pexels)
# ─────────────────────────────────────────────────────────
def telecharger_image(sujet, slug):
    """
    Télécharge une photo libre de droits depuis Pexels selon les mots-clés
    du sujet, la sauvegarde dans images/blog/{slug}.jpg.
    Retourne le chemin relatif de l'image (depuis pages/blog/) ou None.
    Si Pexels échoue, on retourne None et on utilisera l'image de secours.
    """
    pexels_key = os.environ.get("PEXELS_API_KEY")
    query = sujet.get("image_query", "wellness spa")

    if not pexels_key:
        print("  ⚠ PEXELS_API_KEY absente — image de secours utilisée")
        return None

    try:
        # Recherche sur l'API Pexels (paysage, qualité)
        url = (
            "https://api.pexels.com/v1/search?"
            + urllib.parse.urlencode({
                "query": query,
                "orientation": "landscape",
                "per_page": 10,
                "size": "large",
            })
        )
        req = urllib.request.Request(url, headers={"Authorization": pexels_key})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        photos = result.get("photos", [])
        if not photos:
            print(f"  ⚠ Aucune photo Pexels pour « {query} » — image de secours")
            return None

        # On prend la 1ère photo. Pour varier, on pourrait utiliser un index
        # basé sur le slug, mais la recherche renvoie déjà des résultats variés.
        photo = photos[0]
        img_url = photo["src"]["large"]  # ~1880px de large, bonne qualité

        # Télécharger l'image
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        dest = IMAGES_DIR / f"{slug}.jpg"
        img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(img_req, timeout=30) as img_resp:
            dest.write_bytes(img_resp.read())

        # Crédit photographe (bonne pratique Pexels, on le garde en commentaire data)
        photographe = photo.get("photographer", "Pexels")
        print(f"  ✓ Photo Pexels téléchargée (© {photographe}) : images/blog/{slug}.jpg")

        # Tenter une conversion WebP si Pillow est dispo (sinon on garde le JPG)
        try:
            from PIL import Image
            img = Image.open(dest).convert("RGB")
            # Redimensionner si trop large (max 1400px)
            if img.width > 1400:
                ratio = 1400 / img.width
                img = img.resize((1400, int(img.height * ratio)), Image.LANCZOS)
            webp_dest = IMAGES_DIR / f"{slug}.webp"
            img.save(webp_dest, "WEBP", quality=82, method=6)
            dest.unlink()  # supprimer le JPG, garder le WebP
            print(f"  ✓ Converti en WebP : images/blog/{slug}.webp")
            return f"../../images/blog/{slug}.webp"
        except ImportError:
            # Pillow absent : on garde le JPG
            return f"../../images/blog/{slug}.jpg"

    except Exception as e:
        print(f"  ⚠ Erreur téléchargement Pexels : {e} — image de secours")
        return None


# ─────────────────────────────────────────────────────────
# 3. CONSTRUCTION DU FICHIER HTML
# ─────────────────────────────────────────────────────────
def construire_html(sujet, data, slug, image_cover):
    """Génère le HTML complet de l'article à partir du template.
    image_cover : chemin relatif (depuis pages/blog/) de l'image de couverture."""

    maintenant = datetime.now()
    date_fr = f"{MOIS_FR[maintenant.month - 1].capitalize()} {maintenant.year}"
    initiale = sujet["auteur"][0].upper()

    # Bio auteur
    bios = {
        "Charlotte": "Diététicienne-Nutritionniste diplômée depuis 2009. Co-gérante du centre, spécialiste de la nutrition clinique et de l'équilibre hormonal.",
        "Alison": "Esthéticienne diplômée et experte en technologies avancées depuis 2012. Co-gérante du centre, spécialiste des protocoles silhouette et récupération.",
    }
    bio = bios.get(sujet["auteur"], "")

    # Échapper les valeurs pour les attributs meta
    meta_desc = html.escape(data["meta_description"], quote=True)
    titre_plain = html.escape(data["titre"], quote=True)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{titre_plain}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<title>{titre_plain} — Body Reset</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/main.css">
<style>
.article-hero{{padding:140px 0 60px;background:var(--c);position:relative}}
.article-meta{{display:flex;align-items:center;gap:14px;margin-bottom:24px;font-size:.82rem;color:var(--mu);flex-wrap:wrap}}
.article-cat{{background:var(--tx);color:var(--td);padding:5px 14px;border-radius:100px;font-weight:500;letter-spacing:.04em;font-size:.74rem}}
.article-meta .dot{{opacity:.4}}
.article-hero h1{{font-size:clamp(2rem,4vw,3.5rem);line-height:1.15;margin-bottom:20px;max-width:820px}}
.article-hero .lead{{font-size:1.15rem;color:var(--mu);max-width:740px;line-height:1.7;font-family:var(--fd);font-style:italic;font-weight:300}}

.article-cover{{max-width:1080px;margin:0 auto 60px;padding:0 56px}}
.article-cover-img{{width:100%;aspect-ratio:21/9;background-size:cover;background-position:center;border-radius:var(--rl)}}

.article-body{{max-width:740px;margin:0 auto;padding:0 56px 100px}}
.article-body p{{font-size:1.04rem;line-height:1.85;margin-bottom:22px;color:var(--bm)}}
.article-body h2{{font-size:1.9rem;margin:50px 0 20px;color:var(--br);line-height:1.25}}
.article-body h3{{font-size:1.4rem;margin:36px 0 14px;color:var(--br);font-family:var(--fb);font-weight:600}}
.article-body ul,.article-body ol{{margin:0 0 22px 28px;padding:0}}
.article-body li{{margin-bottom:10px;font-size:1.04rem;line-height:1.7;color:var(--bm)}}
.article-body strong{{color:var(--br);font-weight:600}}
.article-body em{{color:var(--tc);font-style:italic}}
.article-body blockquote{{border-left:3px solid var(--tc);padding:6px 0 6px 24px;margin:30px 0;font-family:var(--fd);font-size:1.4rem;font-style:italic;color:var(--br);line-height:1.5}}
.article-body a{{color:var(--tc);text-decoration:underline;text-decoration-color:var(--tx);text-underline-offset:3px;transition:var(--tf)}}
.article-body a:hover{{text-decoration-color:var(--tc)}}

.callout{{background:var(--cm);border-radius:var(--rm);padding:28px 32px;margin:36px 0;border-left:4px solid var(--sg)}}
.callout strong{{color:var(--sd);display:block;margin-bottom:8px;font-size:.95rem}}
.callout p{{margin:0;font-size:.95rem}}

.related-cta{{background:linear-gradient(135deg,var(--sd) 0%,var(--sg) 100%);color:#fff;padding:48px;border-radius:var(--rl);margin:50px 0;text-align:center}}
.related-cta h3{{color:#fff;font-size:1.5rem;margin-bottom:10px}}
.related-cta p{{color:rgba(255,255,255,.85);margin-bottom:24px;font-size:.95rem}}
.related-cta .btn{{background:#fff;color:var(--sd)}}

.author-box{{display:flex;align-items:center;gap:20px;padding:24px;background:var(--cm);border-radius:var(--rm);margin-top:50px}}
.author-avatar{{width:60px;height:60px;border-radius:50%;background:var(--cd);display:flex;align-items:center;justify-content:center;font-family:var(--fd);font-size:1.8rem;color:var(--tc);font-style:italic;flex-shrink:0}}
.author-info p{{margin:0;font-size:.88rem;color:var(--mu)}}
.author-info strong{{color:var(--br);font-size:.95rem;display:block;margin-bottom:2px}}

@media(max-width:768px){{
  .article-cover,.article-body{{padding-left:24px;padding-right:24px}}
  .article-cover{{margin-bottom:40px}}
  .article-body h2{{font-size:1.55rem}}
  .article-body blockquote{{font-size:1.15rem;padding-left:18px}}
  .related-cta{{padding:32px 24px}}
}}
</style>
</head>
<body data-nav="blog">

<div id="site-header"></div>

<section class="article-hero">
  <div class="wrap">
    <nav class="bread"><a href="../../index.html">Accueil</a><span>›</span><a href="../blog.html">Blog</a><span>›</span><span>{titre_plain}</span></nav>
    <div class="article-meta">
      <span class="article-cat">{html.escape(sujet['categorie'])}</span>
      <span class="dot">·</span>
      <span>{date_fr}</span>
      <span class="dot">·</span>
      <span>{html.escape(data['temps_lecture'])}</span>
      <span class="dot">·</span>
      <span>Par {html.escape(sujet['auteur'])}</span>
    </div>
    <h1>{data['titre_html']}</h1>
    <p class="lead">{data['chapeau']}</p>
  </div>
</section>

<div class="article-cover rv-zoom">
  <div class="article-cover-img" style="background-image:url('{image_cover}')"></div>
</div>

<article class="article-body">

{data['corps_html']}

  <div class="related-cta">
    <h3>Envie d'un accompagnement personnalisé ?</h3>
    <p>Lors de votre bilan offert, nous analysons votre situation et construisons ensemble un protocole sur mesure.</p>
    <a href="../reservation.html" class="btn">Réserver mon bilan offert →</a>
  </div>

  <h2>En résumé</h2>

{data['resume_html']}

  <div class="author-box">
    <div class="author-avatar">{initiale}</div>
    <div class="author-info">
      <strong>{html.escape(sujet['auteur'])}</strong>
      <p>{html.escape(bio)}</p>
    </div>
  </div>
</article>

<div id="site-footer"></div>
<script src="../../js/layout.js"></script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────
# 4. MISE À JOUR DE blog.html (ajout de la carte)
# ─────────────────────────────────────────────────────────
def ajouter_carte_blog(sujet, data, slug, image_card):
    c = BLOG_INDEX.read_text(encoding="utf-8")

    nouvelle_carte = f"""      <a href="blog/{slug}.html" class="bcard">
        <div class="bcard-img"><div class="bcard-img-inner" style="background-image:url('{image_card}')"></div></div>
        <div class="bcard-body">
          <div class="bcard-meta"><span class="bcard-cat">{html.escape(sujet['categorie'])}</span><span>·</span><span>{html.escape(data['temps_lecture'])}</span></div>
          <h3>{html.escape(data['titre'])}</h3>
          <p>{html.escape(data['meta_description'])}</p>
          <span class="bcard-read">Lire l'article →</span>
        </div>
      </a>

"""

    # Insérer juste après l'ouverture de la grille pour que le nouvel article soit en premier
    marqueur = '<div class="blog-grid rv-stagger">\n\n'
    if marqueur in c:
        c = c.replace(marqueur, marqueur + nouvelle_carte)
    else:
        # Fallback : insérer après la div blog-grid sans le double saut de ligne
        marqueur2 = '<div class="blog-grid rv-stagger">'
        c = c.replace(marqueur2, marqueur2 + "\n\n" + nouvelle_carte)

    BLOG_INDEX.write_text(c, encoding="utf-8")


# ─────────────────────────────────────────────────────────
# 5. MISE À JOUR DU SITEMAP
# ─────────────────────────────────────────────────────────
def ajouter_sitemap(slug):
    s = SITEMAP.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{SITE_URL}/pages/blog/{slug}.html"

    if url in s:
        return  # déjà présent

    entree = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
    s = s.replace("</urlset>", entree + "</urlset>")
    SITEMAP.write_text(s, encoding="utf-8")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
def main():
    print("═══ Génération article hebdomadaire Body Reset ═══")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("✗ ANTHROPIC_API_KEY manquante dans l'environnement")
        sys.exit(1)

    calendrier = charger_calendrier()
    sujet = choisir_sujet(calendrier)

    if sujet is None:
        print("ℹ Aucun sujet 'a_publier' dans le calendrier. Rien à faire.")
        print("  → Ajoutez de nouveaux sujets dans automation/calendrier-editorial.json")
        # On sort en code 0 : ce n'est pas une erreur, juste plus de sujets
        sys.exit(0)

    print(f"📝 Sujet choisi : {sujet['id']}")
    print(f"   Catégorie : {sujet['categorie']} · Auteur : {sujet['auteur']}")

    client = anthropic.Anthropic(api_key=api_key)
    data = generer_article(client, sujet)
    print(f"✓ Article généré : « {data['titre']} »")

    slug = sujet["id"]
    fichier = BLOG_DIR / f"{slug}.html"

    # Télécharger une image Pexels unique pour cet article
    image_dl = telecharger_image(sujet, slug)
    if image_dl:
        # image_dl est au format "../../images/blog/{slug}.webp" (depuis pages/blog/)
        image_cover = image_dl
        # Pour la carte sur blog.html (depuis pages/), le chemin est "../images/blog/..."
        image_card = image_dl.replace("../../images/", "../images/")
    else:
        # Image de secours déjà présente sur le site
        image_cover = f"../../images/{IMAGE_FALLBACK}"
        image_card = f"../images/{IMAGE_FALLBACK}"

    html_content = construire_html(sujet, data, slug, image_cover)
    fichier.write_text(html_content, encoding="utf-8")
    print(f"✓ Fichier créé : pages/blog/{slug}.html")

    ajouter_carte_blog(sujet, data, slug, image_card)
    print("✓ blog.html mis à jour (nouvelle carte)")

    ajouter_sitemap(slug)
    print("✓ sitemap.xml mis à jour")

    marquer_publie(calendrier, slug)
    print("✓ Sujet marqué comme publié dans le calendrier")

    # Exposer le titre pour le message de commit (via GITHUB_OUTPUT)
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"article_titre={data['titre']}\n")
            f.write(f"article_slug={slug}\n")

    print("═══ Terminé avec succès ═══")


if __name__ == "__main__":
    main()
