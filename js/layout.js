/* ═══════════════════════════════════════════════════
   CENTRE BODY RESET — JS GLOBAL
   Injecte le header/footer + gère scroll, menu, reveal
═══════════════════════════════════════════════════ */

(function(){

// ── Détermine le préfixe de chemin selon la profondeur de la page ──
// Si la page est dans /pages/blog/article.html, ../../ pour remonter à la racine
function getBasePath(){
  const path = window.location.pathname;
  const depth = (path.match(/\//g) || []).length - 1;
  if(depth <= 0 || path === '/' || path.endsWith('/index.html')) return '';
  return '../'.repeat(depth);
}

const BP = getBasePath();

// ── HTML du Header ──
const HEADER_HTML = `
<nav id="nav">
  <div class="nl"><a href="${BP}index.html"><img src="${BP}images/logo.png" alt="Centre Body Reset"></a></div>
  <ul class="nls">
    <li><a href="${BP}index.html#solutions" data-nav="solutions">Nos solutions</a></li>
    <li><a href="${BP}index.html#technologies" data-nav="technologies">Technologies</a></li>
    <li><a href="${BP}pages/a-propos.html" data-nav="apropos">À propos</a></li>
    <li><a href="${BP}pages/tarifs.html" data-nav="tarifs">Tarifs</a></li>
    <li><a href="${BP}pages/blog.html" data-nav="blog">Blog</a></li>
    <li><a href="${BP}pages/contact.html" data-nav="contact">Contact</a></li>
  </ul>
  <div class="nr">
    <a href="${BP}pages/contact.html" class="btn bp" style="padding:11px 24px;font-size:.82rem;">Réserver mon bilan</a>
  </div>
  <button class="burg" id="burg" aria-label="Menu"><span></span><span></span><span></span></button>
</nav>

<div class="mm" id="mm">
  <a href="${BP}index.html">Accueil</a>
  <a href="${BP}index.html#solutions">Nos solutions</a>
  <a href="${BP}index.html#technologies">Technologies</a>
  <a href="${BP}pages/a-propos.html">À propos</a>
  <a href="${BP}pages/tarifs.html">Tarifs</a>
  <a href="${BP}pages/blog.html">Blog</a>
  <a href="${BP}pages/contact.html">Contact</a>
  <a href="${BP}pages/contact.html" class="btn bp">Réserver mon bilan offert</a>
</div>
`;

// ── HTML du Footer ──
const FOOTER_HTML = `
<footer>
  <div class="wrap">
    <div class="fg">
      <div class="fb">
        <img src="${BP}images/logo.png" alt="Centre Body Reset">
        <p>Centre Body Reset — Clermont-l'Hérault<br>L'alliance unique de la nutrition clinique et des technologies de pointe.</p>
        <div class="fso">
          <a href="https://instagram.com/centre.body.reset" target="_blank" rel="noopener" aria-label="Instagram">📷</a>
          <a href="https://facebook.com" target="_blank" rel="noopener" aria-label="Facebook">📘</a>
          <a href="https://doctolib.fr" target="_blank" rel="noopener" aria-label="Doctolib">🩺</a>
        </div>
      </div>
      <div class="fc">
        <h4>Navigation</h4>
        <ul>
          <li><a href="${BP}index.html">Accueil</a></li>
          <li><a href="${BP}pages/a-propos.html">À propos</a></li>
          <li><a href="${BP}pages/tarifs.html">Tarifs</a></li>
          <li><a href="${BP}pages/blog.html">Blog</a></li>
          <li><a href="${BP}pages/contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="fc">
        <h4>Nos solutions</h4>
        <ul>
          <li><a href="${BP}pages/solutions/silhouette.html">Silhouette &amp; poids</a></li>
          <li><a href="${BP}pages/solutions/menopause.html">Ménopause</a></li>
          <li><a href="${BP}pages/solutions/sommeil.html">Sommeil &amp; vitalité</a></li>
          <li><a href="${BP}pages/solutions/sportifs.html">Récupération sportive</a></li>
          <li><a href="${BP}pages/solutions/bien-etre-urinaire.html">Bien-être urinaire</a></li>
          <li><a href="${BP}pages/solutions/drainage.html">Drainage lymphatique</a></li>
        </ul>
      </div>
      <div class="fc">
        <h4>Technologies</h4>
        <ul>
          <li><a href="${BP}pages/technologies/cryolipolyse.html">Cryolipolyse</a></li>
          <li><a href="${BP}pages/technologies/adipologie.html">Adipologie</a></li>
          <li><a href="${BP}pages/technologies/led.html">LED Infrarouge</a></li>
          <li><a href="${BP}pages/technologies/pressotherapie.html">Pressodynamie</a></li>
          <li><a href="${BP}pages/technologies/chaise-ems.html">Chaise EMS</a></li>
        </ul>
      </div>
    </div>
    <hr class="fdv">
    <a href="https://www.agence-pmc-marketing.com/" target="_blank" rel="noopener" class="pmc-credit">
      <span class="pmc-credit-label">Conçu par</span>
      <img src="${BP}images/pmc-logo.png" alt="PMC Marketing">
    </a>
    <hr class="fdv" style="margin-top:24px">
    <div class="fbt">
      <span class="fbt-credit">© 2026 Centre Body Reset — Tous droits réservés</span>
      <div class="fbl">
        <a href="${BP}pages/mentions-legales.html">Mentions légales</a>
        <a href="${BP}pages/confidentialite.html">Confidentialité</a>
        <a href="${BP}pages/cgv.html">CGV</a>
      </div>
    </div>
  </div>
</footer>
`;

// ── Injection : on ajoute le header en début de body et le footer en fin ──
const headerEl = document.getElementById('site-header');
const footerEl = document.getElementById('site-footer');
if(headerEl){ headerEl.outerHTML = HEADER_HTML; }
if(footerEl){ footerEl.outerHTML = FOOTER_HTML; }

// ── Active le lien de navigation correspondant à la page courante ──
const currentNav = document.body.dataset.nav;
if(currentNav){
  document.querySelectorAll(`[data-nav="${currentNav}"]`).forEach(a => a.classList.add('active'));
}

// ── Nav scroll (fond blanc) ──
const nav = document.getElementById('nav');
function updateNav(){
  if(!nav) return;
  if(window.scrollY > 10){
    nav.classList.add('sc');
    nav.style.background = '#ffffff';
    nav.style.boxShadow = '0 4px 20px rgba(42,32,27,.08)';
    nav.style.padding = '13px 40px';
    nav.style.borderBottom = '1px solid rgba(42,32,27,.05)';
  } else {
    nav.classList.remove('sc');
    nav.style.background = '';
    nav.style.boxShadow = '';
    nav.style.padding = '';
    nav.style.borderBottom = '';
  }
}
window.addEventListener('scroll', updateNav, {passive:true});
window.addEventListener('load', updateNav);
window.addEventListener('resize', updateNav, {passive:true});
updateNav();

// ── Menu mobile ──
const burg = document.getElementById('burg');
const mm = document.getElementById('mm');
let mobileOpen = false;
function closeMobile(){
  mobileOpen = false;
  if(mm) mm.classList.remove('op');
  document.body.style.overflow = '';
  if(burg) burg.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
}
if(burg && mm){
  burg.addEventListener('click', () => {
    mobileOpen = !mobileOpen;
    mm.classList.toggle('op', mobileOpen);
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    burg.querySelectorAll('span').forEach((s, i) => {
      if(mobileOpen){
        if(i === 0) s.style.transform = 'translateY(6px) rotate(45deg)';
        if(i === 1) s.style.opacity = '0';
        if(i === 2) s.style.transform = 'translateY(-6px) rotate(-45deg)';
      } else {
        s.style.transform = ''; s.style.opacity = '';
      }
    });
  });
  mm.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMobile));
}

// ── Reveal au scroll ──
function checkReveal(){
  const elements = document.querySelectorAll('.rv, .rv-left, .rv-right, .rv-scale, .rv-zoom, .rv-stagger');
  const trigger = window.innerHeight * 0.88;
  elements.forEach(el => {
    if(el.classList.contains('shown')) return;
    const rect = el.getBoundingClientRect();
    if(rect.top < trigger && rect.bottom > 0){
      el.classList.add('shown');
    }
  });
}
let ticking = false;
window.addEventListener('scroll', () => {
  if(!ticking){
    requestAnimationFrame(() => { checkReveal(); ticking = false; });
    ticking = true;
  }
}, {passive:true});
window.addEventListener('resize', checkReveal, {passive:true});
window.addEventListener('load', checkReveal);
document.addEventListener('DOMContentLoaded', checkReveal);
checkReveal();

// ── Smooth anchors ──
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const href = a.getAttribute('href');
    if(href === '#' || href.length < 2) return;
    const t = document.querySelector(href);
    if(t){
      e.preventDefault();
      window.scrollTo({top: t.offsetTop - 80, behavior:'smooth'});
    }
  });
});

})();
