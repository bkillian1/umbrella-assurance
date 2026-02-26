import streamlit as st
import os
import base64

# ─────────────────────────────────────────────
# 1. CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Umbrella Assurance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# 2. DONNÉES ACTUARIELLES (source : Excel)
# ─────────────────────────────────────────────
# Primes pures par âge (65–94) : (densité forte, densité faible)
PRIMES_PURES = {
    65: (22.58, 32.08),  66: (24.73, 32.08),  67: (28.00, 32.08),
    68: (32.70, 34.41),  69: (38.50, 40.43),  70: (45.88, 49.39),
    71: (53.56, 61.09),  72: (63.22, 75.76),  73: (77.47, 96.00),
    74: (95.06, 118.04), 75: (116.10, 137.53), 76: (140.11, 158.64),
    77: (167.02, 178.29), 78: (196.99, 197.83), 79: (229.68, 229.68),
    80: (261.17, 270.58), 81: (296.53, 322.34), 82: (337.22, 380.01),
    83: (384.89, 448.16), 84: (439.86, 535.27), 85: (506.18, 631.85),
    86: (598.53, 729.04), 87: (699.62, 835.34), 88: (798.15, 961.34),
    89: (902.44, 1094.13), 90: (1013.60, 1226.23), 91: (1130.73, 1361.76),
    92: (1252.75, 1497.89), 93: (1380.25, 1636.81), 94: (1513.21, 1778.48)
}
TAUX_MARGE  = {'forte': 0.18, 'faible': 0.20}
TAUX_FRAIS  = 0.15   # Autres paramètres!C8


def calcul_prime_commerciale(age: int, densite: str) -> tuple[float, float, float]:
    """Retourne (prime_pure, chargements, prime_commerciale) en €/an."""
    idx         = 0 if densite == 'forte' else 1
    prime_pure  = PRIMES_PURES[age][idx]
    taux_marge  = TAUX_MARGE[densite]
    prime_com   = prime_pure * (1 + taux_marge) / (1 - TAUX_FRAIS)
    chargements = prime_com - prime_pure
    return prime_pure, chargements, prime_com


# ─────────────────────────────────────────────
# 3. CSS — STYLE PREMIUM / HAUT DE GAMME
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Page ── */
.stApp {
    background-color: #f5f6fa;
    font-family: 'Inter', sans-serif;
    color: #0d1b2a;
}

/* ── Masquer les éléments Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
div[data-testid="stDecoration"] { display: none; }

/* ══════════════════════════════════════
   NAVBAR
══════════════════════════════════════ */
.navbar {
    background: #ffffff;
    box-shadow: 0 1px 16px rgba(13,27,42,0.09);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 3rem;
    height: 74px;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 2px solid #c8a84b;
}
.navbar-logo img   { height: 52px; object-fit: contain; }
.navbar-logo-text  {
    font-family: 'Raleway', sans-serif;
    font-weight: 900;
    font-size: 1.45rem;
    color: #0d1b2a;
    letter-spacing: 1.5px;
}
.navbar-logo-text span { color: #c8a84b; }

.navbar-menu {
    display: flex;
    align-items: center;
    gap: 2.5rem;
}
.navbar-menu a {
    font-family: 'Inter', sans-serif;
    font-size: 0.87rem;
    font-weight: 500;
    color: #374151;
    text-decoration: none;
    letter-spacing: 0.3px;
    transition: color 0.2s;
}
.navbar-menu a:hover { color: #1e3a8a; }

.navbar-cta {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.btn-client {
    background: #991b1b;
    color: #ffffff !important;
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 0.6px;
    padding: 0.6rem 1.4rem;
    border-radius: 3px;
    text-decoration: none;
    transition: background 0.2s;
    white-space: nowrap;
}
.btn-client:hover { background: #7f1d1d; }

/* ══════════════════════════════════════
   HERO
══════════════════════════════════════ */
.hero {
    background: linear-gradient(125deg, #0d1b2a 0%, #1a3356 55%, #1e3a8a 100%);
    min-height: 500px;
    display: flex;
    align-items: center;
    padding: 4rem 5rem;
    position: relative;
    overflow: hidden;
}

/* Cercles décoratifs */
.hero::before {
    content: '';
    position: absolute;
    right: -100px; top: -100px;
    width: 500px; height: 500px;
    border-radius: 50%;
    background: rgba(200,168,75,0.06);
}
.hero::after {
    content: '';
    position: absolute;
    right: 200px; bottom: -150px;
    width: 350px; height: 350px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 580px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(200,168,75,0.15);
    border: 1px solid rgba(200,168,75,0.4);
    color: #c8a84b;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.4rem 1rem;
    border-radius: 2px;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-family: 'Raleway', sans-serif;
    font-weight: 800;
    font-size: 2.9rem;
    line-height: 1.15;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.hero-divider {
    width: 64px;
    height: 3px;
    background: #c8a84b;
    margin: 1.2rem 0;
    border-radius: 2px;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 300;
    color: rgba(255,255,255,0.75);
    line-height: 1.65;
    margin-bottom: 2rem;
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    flex-wrap: wrap;
}

.btn-hero-primary {
    background: #c8a84b;
    color: #0d1b2a !important;
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 0.92rem;
    letter-spacing: 0.5px;
    padding: 0.9rem 2.2rem;
    border-radius: 3px;
    text-decoration: none;
    transition: all 0.2s;
    display: inline-block;
}
.btn-hero-primary:hover { background: #a8882f; transform: translateY(-1px); }

.btn-hero-secondary {
    color: rgba(255,255,255,0.8) !important;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.35);
    padding-bottom: 2px;
    transition: all 0.2s;
}
.btn-hero-secondary:hover { color: #fff !important; border-color: rgba(255,255,255,0.8); }

.hero-trust {
    position: absolute;
    right: 5rem;
    bottom: 3rem;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.trust-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 6px;
    padding: 0.7rem 1.2rem;
}
.trust-icon { font-size: 1.3rem; }
.trust-text { color: rgba(255,255,255,0.85); font-size: 0.82rem; font-weight: 500; }
.trust-text strong { color: #ffffff; display: block; font-size: 1rem; }

/* ══════════════════════════════════════
   SECTION TITRE GÉNÉRIQUE
══════════════════════════════════════ */
.section-header {
    text-align: center;
    margin-bottom: 3rem;
}
.section-header h2 {
    font-family: 'Raleway', sans-serif;
    font-weight: 800;
    font-size: 1.85rem;
    color: #0d1b2a;
    margin-bottom: 0.5rem;
}
.section-header .gold-line {
    width: 48px;
    height: 3px;
    background: #c8a84b;
    margin: 0.6rem auto;
    border-radius: 2px;
}
.section-header p {
    color: #64748b;
    font-size: 1rem;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ══════════════════════════════════════
   SECTION SOLUTIONS
══════════════════════════════════════ */
.solutions-section {
    background: #ffffff;
    padding: 4.5rem 5rem;
    border-bottom: 1px solid #e9ecf5;
}

.solutions-grid {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.solution-card {
    background: #f8f9fc;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.8rem 1.6rem;
    min-width: 170px;
    flex: 1;
    max-width: 210px;
    text-align: center;
    transition: all 0.25s ease;
    cursor: pointer;
    position: relative;
}
.solution-card:hover {
    border-color: #1e3a8a;
    box-shadow: 0 6px 24px rgba(30,58,138,0.1);
    transform: translateY(-3px);
}
.solution-card.featured {
    border-color: #c8a84b;
    background: #fffdf5;
}
.solution-card.featured:hover { border-color: #a8882f; }

.card-badge {
    position: absolute;
    top: -11px;
    left: 50%;
    transform: translateX(-50%);
    background: #c8a84b;
    color: #0d1b2a;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    white-space: nowrap;
}

.solution-card .icon {
    font-size: 2rem;
    margin-bottom: 0.8rem;
}
.solution-card h3 {
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #0d1b2a;
    margin-bottom: 0.4rem;
}
.solution-card p {
    font-size: 0.79rem;
    color: #64748b;
    line-height: 1.55;
}

/* ══════════════════════════════════════
   COMMENT ÇA MARCHE
══════════════════════════════════════ */
.howto-section {
    background: #f5f6fa;
    padding: 4.5rem 5rem;
    border-bottom: 1px solid #e9ecf5;
}

.howto-steps {
    display: flex;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.howto-step {
    flex: 1;
    min-width: 240px;
    max-width: 300px;
    text-align: center;
    padding: 1rem;
}

.step-number {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #0d1b2a;
    border: 2px solid #c8a84b;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Raleway', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: #c8a84b;
    margin-bottom: 1.2rem;
}

.howto-step h3 {
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #0d1b2a;
    margin-bottom: 0.5rem;
}
.howto-step p {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.6;
}

.howto-connector {
    display: flex;
    align-items: center;
    padding-top: 1.5rem;
    color: #c8a84b;
    font-size: 1.5rem;
    font-weight: 300;
}

/* ══════════════════════════════════════
   CALCULATEUR DE PRIME
══════════════════════════════════════ */
.devis-section {
    background: #ffffff;
    padding: 4.5rem 5rem;
    border-bottom: 1px solid #e9ecf5;
}

/* Inputs Streamlit */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border: 1.5px solid #d1d9e8 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    background: #fafbff !important;
    color: #0d1b2a !important;
    font-size: 0.95rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #1e3a8a !important;
    box-shadow: 0 0 0 3px rgba(30,58,138,0.1) !important;
}
div[data-testid="stSelectbox"] > div {
    border: 1.5px solid #d1d9e8 !important;
    border-radius: 6px !important;
    background: #fafbff !important;
}

/* Labels */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #374151 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* Bouton principal */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button {
    background: #1e3a8a !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: 'Raleway', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.8rem !important;
    transition: background 0.2s !important;
    width: 100%;
}
div[data-testid="stButton"] > button:hover {
    background: #1e40af !important;
}

/* Résultat devis */
.result-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a3356 100%);
    border: 1px solid rgba(200,168,75,0.3);
    border-radius: 10px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    color: #ffffff;
}
.result-card .result-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #c8a84b;
    margin-bottom: 1rem;
}
.result-card .result-price {
    font-family: 'Raleway', sans-serif;
    font-size: 3rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
}
.result-card .result-price span {
    font-size: 1.1rem;
    font-weight: 400;
    color: rgba(255,255,255,0.65);
    margin-left: 0.3rem;
}
.result-breakdown {
    display: flex;
    gap: 1.5rem;
    margin-top: 1.2rem;
    padding-top: 1.2rem;
    border-top: 1px solid rgba(255,255,255,0.12);
    flex-wrap: wrap;
}
.breakdown-item {
    display: flex;
    flex-direction: column;
}
.breakdown-label {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 2px;
}
.breakdown-val {
    font-family: 'Raleway', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: rgba(255,255,255,0.9);
}

/* ══════════════════════════════════════
   TÉMOIGNAGES
══════════════════════════════════════ */
.temoignages-section {
    background: #f5f6fa;
    padding: 4.5rem 5rem;
    border-bottom: 1px solid #e9ecf5;
}

.temoignages-grid {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.temoignage-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #c8a84b;
    border-radius: 8px;
    padding: 1.8rem;
    flex: 1;
    min-width: 260px;
    max-width: 360px;
    box-shadow: 0 2px 12px rgba(13,27,42,0.05);
}
.temoignage-stars { color: #c8a84b; font-size: 0.9rem; margin-bottom: 0.8rem; }
.temoignage-text {
    font-size: 0.88rem;
    color: #374151;
    line-height: 1.65;
    font-style: italic;
    margin-bottom: 1.2rem;
}
.temoignage-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.author-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #1e3a8a;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 1rem;
}
.author-name {
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 0.87rem;
    color: #0d1b2a;
}
.author-info {
    font-size: 0.76rem;
    color: #64748b;
}

/* ══════════════════════════════════════
   FAQ
══════════════════════════════════════ */
.faq-section {
    background: #ffffff;
    padding: 4.5rem 5rem;
    border-bottom: 1px solid #e9ecf5;
}

/* Expanders Streamlit */
div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    margin-bottom: 0.6rem !important;
    background: #fafbff !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Raleway', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.97rem !important;
    color: #0d1b2a !important;
    padding: 1rem 1.2rem !important;
}
div[data-testid="stExpander"] summary:hover {
    background: #f0f4ff !important;
}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 0 1.2rem 1rem !important;
    font-size: 0.88rem !important;
    color: #374151 !important;
    line-height: 1.65 !important;
}

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.footer-main {
    background: #0d1b2a;
    color: rgba(255,255,255,0.5);
    text-align: center;
    padding: 2.5rem 2rem 1.2rem;
    font-size: 0.82rem;
    letter-spacing: 0.3px;
}
.footer-logo-text {
    font-family: 'Raleway', sans-serif;
    font-weight: 900;
    font-size: 1.2rem;
    color: #ffffff;
    letter-spacing: 1.5px;
    margin-bottom: 0.3rem;
}
.footer-logo-text span { color: #c8a84b; }
.footer-tagline {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.4);
    margin-bottom: 1.5rem;
}
.footer-links {
    margin-bottom: 1rem;
}
.footer-links a {
    color: rgba(255,255,255,0.5);
    text-decoration: none;
    margin: 0 0.8rem;
    transition: color 0.2s;
    font-size: 0.8rem;
}
.footer-links a:hover { color: #c8a84b; }
.footer-copy {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.25);
    margin-top: 0.8rem;
}
.footer-contact-zone {
    background: #0d1b2a;
    display: flex;
    justify-content: center;
    padding: 0 0 2rem;
}

/* Bouton Contact dans le footer */
div[data-testid="stButton"]:has(button[kind="secondary"]) {
    background: #0d1b2a;
    display: flex;
    justify-content: center;
    padding: 0 0 2rem;
}
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(200,168,75,0.4) !important;
    color: rgba(200,168,75,0.8) !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    padding: 5px 22px !important;
    transition: all 0.2s !important;
    min-width: 0 !important;
    width: auto !important;
    font-family: 'Inter', sans-serif !important;
}
button[kind="secondary"]:hover {
    background: rgba(200,168,75,0.1) !important;
    color: #c8a84b !important;
    border-color: rgba(200,168,75,0.8) !important;
}

/* ══════════════════════════════════════
   RESPONSIVE MOBILE  (≤ 768px)
══════════════════════════════════════ */
@media (max-width: 768px) {

    /* ── Navbar ── */
    .navbar {
        padding: 0 1rem;
        height: 60px;
    }
    .navbar-menu { display: none; }   /* menu masqué sur mobile */
    .navbar-logo img { height: 40px; }
    .btn-client {
        font-size: 0.72rem;
        padding: 0.45rem 0.9rem;
    }

    /* ── Hero ── */
    .hero {
        padding: 2.5rem 1.2rem 10rem;
        min-height: auto;
    }
    .hero-title { font-size: 1.8rem; }
    .hero-subtitle { font-size: 0.93rem; }
    .hero-trust {
        position: static;
        flex-direction: column;
        gap: 0.6rem;
        margin-top: 1.8rem;
    }
    .trust-item { width: 100%; }
    .btn-hero-primary { font-size: 0.85rem; padding: 0.75rem 1.5rem; }

    /* ── Sections padding ── */
    .solutions-section,
    .howto-section,
    .devis-section,
    .temoignages-section,
    .faq-section {
        padding: 2.5rem 1.2rem;
    }

    /* ── Section header ── */
    .section-header h2 { font-size: 1.4rem; }

    /* ── Solutions : 2 colonnes sur mobile ── */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.8rem !important;
    }
    div[data-testid="stColumn"] {
        min-width: 45% !important;
        flex: 1 1 45% !important;
    }
    .solution-card { max-width: 100%; min-width: 0; }

    /* ── Comment ça marche : colonne unique ── */
    .howto-connector { display: none; }
    .howto-step { min-width: 100%; text-align: center; }

    /* ── Résultat devis ── */
    .result-card { padding: 1.4rem; }
    .result-card .result-price { font-size: 2.2rem; }
    .result-breakdown { gap: 0.8rem; }

    /* ── Témoignages : une carte visible en pleine largeur ── */
    .temoignage-card { max-width: 100%; min-width: 0; }

    /* ── Footer ── */
    .footer-main { padding: 2rem 1rem 1rem; }
    .footer-links a { display: block; margin: 0.4rem 0; }

    /* ── Vidéo ── */
    div[data-testid="stVideo"] { width: 100% !important; }
}

/* ══════════════════════════════════════
   RESPONSIVE TABLETTE  (769px – 1024px)
══════════════════════════════════════ */
@media (min-width: 769px) and (max-width: 1024px) {

    .navbar { padding: 0 1.5rem; }
    .navbar-menu { gap: 1.2rem; }

    .hero { padding: 3rem 2rem 6rem; }
    .hero-title { font-size: 2.2rem; }
    .hero-trust { right: 2rem; bottom: 2rem; }

    .solutions-section,
    .howto-section,
    .devis-section,
    .temoignages-section,
    .faq-section {
        padding: 3rem 2rem;
    }

    .solution-card { min-width: 130px; }
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 4. UTILITAIRE LOGO
# ─────────────────────────────────────────────
def get_logo_b64(path="assets/Logo.jpg"):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = (
    f'<img src="data:image/jpeg;base64,{logo_b64}" alt="Umbrella"/>'
    if logo_b64
    else '<div class="navbar-logo-text">UMBRELLA<span>.</span></div>'
)


# ─────────────────────────────────────────────
# 5. NAVBAR
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="navbar">
  <div class="navbar-logo">
    {logo_html}
  </div>
  <nav class="navbar-menu">
    <a href="#solutions">Nos solutions</a>
    <a href="#devis">Tarif</a>
    <a href="#faq">FAQ</a>
  </nav>
  <div class="navbar-cta">
    <a class="btn-client" href="#">🔒 Espace client</a>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 5b. DISCLAIMER ACADÉMIQUE
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: #1e3a8a;
    padding: 0.6rem 1.5rem;
    text-align: center;
    font-family: Inter, sans-serif;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.9);
    letter-spacing: 0.2px;
    border-bottom: 1px solid rgba(200,168,75,0.3);
">
  &#127891;&nbsp;
  <strong style="color:#c8a84b;">Projet acad&#233;mique — M1 Assurance et Gestion des Risques</strong>
  &nbsp;&#183;&nbsp;
  Ce site est une simulation r&#233;alis&#233;e dans le cadre d&#39;un projet p&#233;dagogique.
  Les tarifs affich&#233;s sont calcul&#233;s &#224; partir de donn&#233;es actuarielles r&#233;elles mais ne constituent pas une offre commerciale.
  &nbsp;&#183;&nbsp;
  <strong style="color:#c8a84b;">Umbrella Assurance n&#39;est pas une vraie compagnie d&#39;assurance.</strong>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 6. HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-content">
    <div class="hero-badge">🛡️ Mutuelle Santé Senior</div>
    <h1 class="hero-title">Protégez votre santé.<br>Vivez sereinement.</h1>
    <div class="hero-divider"></div>
    <p class="hero-subtitle">
      Une protection santé sur mesure, conçue spécialement pour les seniors.<br>
      Calculez votre prime en moins d'une minute.
    </p>
    <div class="hero-actions">
      <a class="btn-hero-primary" href="#devis">Obtenir mon tarif gratuit</a>
      <a class="btn-hero-secondary" href="#solutions">Découvrir nos offres ›</a>
    </div>
  </div>
  <div class="hero-trust">
    <div class="trust-item">
      <span class="trust-icon">🏆</span>
      <div class="trust-text">
        <strong>+12 000</strong>
        assurés nous font confiance
      </div>
    </div>
    <div class="trust-item">
      <span class="trust-icon">✅</span>
      <div class="trust-text">
        <strong>Certifié ACPR</strong>
        Autorité de Contrôle Prudentiel
      </div>
    </div>
    <div class="trust-item">
      <span class="trust-icon">📞</span>
      <div class="trust-text">
        <strong>Rappel sous 24h</strong>
        par un conseiller dédié
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 7. NOS SOLUTIONS
# ─────────────────────────────────────────────
st.markdown('<div id="solutions"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="solutions-section">
  <div class="section-header">
    <h2>Nos solutions d&#39;assurance</h2>
    <div class="gold-line"></div>
    <p>Un accompagnement complet pour tous vos besoins de protection.</p>
  </div>
</div>
""", unsafe_allow_html=True)

SOLUTIONS = [
    {
        "icon": "&#127973;",
        "titre": "Sant&#233; Senior",
        "desc": "Mutuelle d&#233;di&#233;e aux 65&#8211;94 ans, avec une prime calcul&#233;e sur des bases actuarielles rigoureuses.",
        "featured": True,
        "badge": "Notre offre phare",
    },
    {
        "icon": "&#128663;",
        "titre": "Auto",
        "desc": "Couverture tous risques ou au tiers, adapt&#233;e &#224; votre usage quotidien.",
        "featured": False,
        "badge": None,
    },
    {
        "icon": "&#127968;",
        "titre": "Habitation",
        "desc": "Prot&#233;gez votre domicile contre les sinistres avec une couverture compl&#232;te.",
        "featured": False,
        "badge": None,
    },
    {
        "icon": "&#128106;",
        "titre": "Famille",
        "desc": "Une protection globale pour chaque membre de votre foyer.",
        "featured": False,
        "badge": None,
    },
    {
        "icon": "&#128200;",
        "titre": "&#201;pargne",
        "desc": "Faites fructifier votre patrimoine avec nos solutions d&#39;&#233;pargne s&#233;curis&#233;es.",
        "featured": False,
        "badge": None,
    },
]

sol_cols = st.columns(5)
for col, s in zip(sol_cols, SOLUTIONS):
    featured_class = "solution-card featured" if s["featured"] else "solution-card"
    badge_html = f'<div class="card-badge">{s["badge"]}</div>' if s["badge"] else ""
    with col:
        st.markdown(f"""
<div class="{featured_class}">
  {badge_html}
  <div class="icon">{s['icon']}</div>
  <h3>{s['titre']}</h3>
  <p>{s['desc']}</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 8. COMMENT ÇA MARCHE
# ─────────────────────────────────────────────
st.markdown("""
<div class="howto-section">
  <div class="section-header">
    <h2>Comment &#231;a marche ?</h2>
    <div class="gold-line"></div>
    <p>En trois &#233;tapes simples, b&#233;n&#233;ficiez d&#39;une couverture sant&#233; adapt&#233;e &#224; votre profil.</p>
  </div>
</div>
""", unsafe_allow_html=True)

HOWTO_STEPS = [
    {
        "num": "1",
        "titre": "Obtenez votre devis",
        "desc": "Renseignez votre &#226;ge et votre zone g&#233;ographique. Notre moteur de calcul actuariel vous donne votre prime personnalis&#233;e en moins de 60 secondes.",
    },
    {
        "num": "2",
        "titre": "Choisissez votre formule",
        "desc": "Un conseiller Umbrella vous contacte sous 24h pour affiner votre contrat et r&#233;pondre &#224; toutes vos questions.",
    },
    {
        "num": "3",
        "titre": "Profitez de vos garanties",
        "desc": "Votre contrat est activ&#233; sans d&#233;lai. Vous b&#233;n&#233;ficiez imm&#233;diatement de votre couverture sant&#233; senior.",
    },
]

hw_col1, hw_arr1, hw_col2, hw_arr2, hw_col3 = st.columns([3, 1, 3, 1, 3])
for col, arr, step in zip(
    [hw_col1, hw_col2, hw_col3],
    [hw_arr1, hw_arr2, None],
    HOWTO_STEPS,
):
    with col:
        st.markdown(f"""
<div class="howto-step">
  <div class="step-number">{step['num']}</div>
  <h3>{step['titre']}</h3>
  <p>{step['desc']}</p>
</div>
""", unsafe_allow_html=True)
    if arr is not None:
        with arr:
            st.markdown(
                '<div class="howto-connector" style="padding-top:1.8rem;text-align:center;">&#8594;</div>',
                unsafe_allow_html=True
            )


# ─────────────────────────────────────────────
# 9. SECTION PUB VIDÉO (auto-détection)
# ─────────────────────────────────────────────
# Déposez n'importe quel fichier .mp4 ou .mov dans assets/
# Il sera détecté et affiché automatiquement.
def find_video(folder="assets"):
    if not os.path.isdir(folder):
        return None
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith((".mp4", ".mov")) and not f.startswith("."):
            return os.path.join(folder, f)
    return None

video_found = find_video()

st.markdown("""
<div style="
    background: #0d1b2a;
    padding: 3.5rem 5rem 0 5rem;
    border-top: 3px solid #c8a84b;
">
  <div style="text-align:center; margin-bottom:1.5rem;">
    <h2 style="
        font-family:Raleway,sans-serif;
        font-weight:800;
        font-size:1.85rem;
        color:#ffffff;
        margin-bottom:0.4rem;
    ">Notre concept en vid&#233;o</h2>
    <div style="width:48px;height:3px;background:#c8a84b;margin:0.5rem auto 0.8rem;border-radius:2px;"></div>
    <p style="color:rgba(255,255,255,0.55);font-size:1rem;font-family:Inter,sans-serif;margin:0;">
      D&#233;couvrez Umbrella Assurance et notre vision de la protection senior.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

if video_found:
    col_vl, col_v, col_vr = st.columns([1, 5, 1])
    with col_v:
        st.markdown(
            '<div style="background:#0d1b2a;padding:0 0 0.5rem;">',
            unsafe_allow_html=True
        )
        st.video(video_found)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("""
<div style="
    background:#0d1b2a;
    padding:2.5rem 5rem;
    text-align:center;
">
  <p style="
    color:rgba(255,255,255,0.3);
    font-size:0.85rem;
    font-family:Inter,sans-serif;
    margin:0;
    border:1px dashed rgba(200,168,75,0.25);
    padding:1.2rem 2rem;
    border-radius:6px;
    display:inline-block;
  ">
    &#127916;&nbsp; D&#233;posez votre fichier <strong style="color:rgba(200,168,75,0.6);">.mp4</strong>
    ou <strong style="color:rgba(200,168,75,0.6);">.mov</strong>
    dans le dossier <code>assets/</code> — il apparaitra ici automatiquement.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div style="background:#0d1b2a;height:3rem;border-bottom:3px solid #c8a84b;"></div>',
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
# 10b. CALCULATEUR DE PRIME ACTUARIEL
# ─────────────────────────────────────────────
st.markdown('<div id="devis"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="devis-section">
  <div class="section-header">
    <h2>Estimez votre prime</h2>
    <div class="gold-line"></div>
    <p>Notre calculateur intègre les données actuarielles du marché pour vous offrir un tarif précis et transparent.</p>
  </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    col_l, col_form, col_r = st.columns([1, 2, 1])
    with col_form:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("👤 Votre Prénom", placeholder="ex : Marie-Claire")
            with col2:
                age = st.number_input(
                    "🎂 Votre Âge",
                    min_value=65, max_value=94, value=70,
                    help="Notre offre Santé Senior est disponible de 65 à 94 ans."
                )

            zone_label = st.selectbox(
                "📍 Votre zone géographique",
                ["Grande ville / Zone urbaine (densité médicale forte)",
                 "Zone rurale / Petite ville (densité médicale faible)"],
                help="La densité médicale de votre zone influence le calcul de votre prime."
            )
            densite = 'forte' if 'forte' in zone_label else 'faible'

            st.write("")
            calc_button = st.button("CALCULER MA PRIME GRATUITE", use_container_width=True)

        if calc_button:
            if nom.strip():
                prime_pure, chargements, prime_com = calcul_prime_commerciale(age, densite)
                st.balloons()
                st.markdown(f"""
<div class="result-card">
  <div class="result-name">Offre personnalisée pour {nom.strip()}</div>
  <div class="result-price">{prime_com:.2f} <span>€ / an</span></div>
  <div class="result-breakdown">
    <div class="breakdown-item">
      <span class="breakdown-label">Prime pure</span>
      <span class="breakdown-val">{prime_pure:.2f} €</span>
    </div>
    <div class="breakdown-item">
      <span class="breakdown-label">Chargements</span>
      <span class="breakdown-val">{chargements:.2f} €</span>
    </div>
    <div class="breakdown-item">
      <span class="breakdown-label">Taux de frais</span>
      <span class="breakdown-val">15 %</span>
    </div>
    <div class="breakdown-item">
      <span class="breakdown-label">Zone</span>
      <span class="breakdown-val">Densité {'forte' if densite == 'forte' else 'faible'}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
                st.info("📞 Un conseiller Umbrella vous rappelle sous 24h pour finaliser votre contrat.")
            else:
                st.error("⚠️ Merci de renseigner votre prénom pour obtenir votre devis personnalisé.")


# ─────────────────────────────────────────────
# 11. TÉMOIGNAGES CLIENTS
# ─────────────────────────────────────────────
st.markdown("""
<div class="temoignages-section">
  <div class="section-header">
    <h2>Ce que nos assurés disent</h2>
    <div class="gold-line"></div>
    <p>Des milliers de seniors nous font confiance chaque jour.</p>
  </div>
</div>
""", unsafe_allow_html=True)

TEMOIGNAGES = [
    {
        "stars": 5,
        "text": "Depuis que j'ai souscrit a Umbrella, je n'ai plus de mauvaises surprises sur mes remboursements. Le tarif est clair, le conseiller etait a l'ecoute. Je recommande vivement.",
        "initiale": "M",
        "nom": "Marie-Claire B.",
        "info": "72 ans &mdash; Toulouse",
    },
    {
        "stars": 5,
        "text": "Le simulateur en ligne m'a permis d'avoir une idee precise de ma prime en quelques secondes. Tres appreciable de voir la decomposition du tarif. Transparent et professionnel.",
        "initiale": "J",
        "nom": "Jean-Pierre L.",
        "info": "68 ans &mdash; Lyon",
    },
    {
        "stars": 4,
        "text": "Apres avoir compare plusieurs mutuelles, Umbrella s'est imposee par la clarte de ses garanties. Mon contrat a ete active tres rapidement. Excellente experience.",
        "initiale": "C",
        "nom": "Colette M.",
        "info": "79 ans &mdash; Bordeaux",
    },
]

col1, col2, col3 = st.columns(3)
for col, t in zip([col1, col2, col3], TEMOIGNAGES):
    stars_full = "&#9733;" * t["stars"] + "&#9734;" * (5 - t["stars"])
    with col:
        st.markdown(f"""
<div class="temoignage-card">
  <div class="temoignage-stars">{stars_full}</div>
  <p class="temoignage-text">{t['text']}</p>
  <div class="temoignage-author">
    <div class="author-avatar">{t['initiale']}</div>
    <div>
      <div class="author-name">{t['nom']}</div>
      <div class="author-info">{t['info']}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 11. FAQ
# ─────────────────────────────────────────────
st.markdown('<div id="faq"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="faq-section">
  <div class="section-header">
    <h2>Questions fréquentes</h2>
    <div class="gold-line"></div>
    <p>Toutes les réponses pour mieux comprendre votre couverture santé senior.</p>
  </div>
</div>
""", unsafe_allow_html=True)

col_l, col_faq, col_r = st.columns([1, 3, 1])
with col_faq:
    with st.expander("Qui peut souscrire à Umbrella Santé Senior ?"):
        st.markdown("""
Notre offre Santé Senior est accessible à toute personne âgée de **65 à 94 ans**, résidant en France métropolitaine.
Aucun questionnaire médical n'est requis pour les tranches d'âge inférieures à 80 ans.
        """)

    with st.expander("Comment est calculée ma prime mensuelle ?"):
        st.markdown("""
Votre prime commerciale est calculée selon la formule actuarielle suivante :

> **Prime commerciale = Prime pure × (1 + Taux de marge) / (1 − Taux de frais)**

- **Prime pure** : coût réel du risque estimé pour votre âge et votre zone géographique
- **Taux de marge** : 18% en zone urbaine, 20% en zone rurale
- **Taux de frais** : 15% (frais de gestion et distribution)

Cette méthode garantit un tarif transparent et équitable.
        """)

    with st.expander("Quel est le délai de carence ?"):
        st.markdown("""
Il n'existe **aucun délai de carence** pour les soins courants (médecin généraliste, pharmacie).
Pour les soins dentaires et optiques, un délai de carence de **3 mois** s'applique à compter de la date d'effet du contrat.
        """)

    with st.expander("Puis-je choisir librement mon médecin ?"):
        st.markdown("""
Oui, Umbrella Santé Senior respecte le principe de **libre choix du praticien**.
Vous pouvez consulter le médecin de votre choix, généraliste ou spécialiste, sans contrainte de réseau.
        """)

    with st.expander("Comment résilier mon contrat ?"):
        st.markdown("""
Vous pouvez résilier votre contrat à tout moment après la première année, en respectant un **préavis de 2 mois**.
Il vous suffit d'envoyer une lettre recommandée avec accusé de réception à notre siège social.
La loi Chatel vous garantit également le droit de résiliation à l'échéance annuelle.
        """)


# ─────────────────────────────────────────────
# 12. FOOTER + EASTER EGG
# ─────────────────────────────────────────────
if "easter_open" not in st.session_state:
    st.session_state.easter_open = False

st.markdown("""
<div class="footer-main">
  <div class="footer-logo-text">UMBRELLA<span>.</span></div>
  <div class="footer-tagline">La mutuelle senior de confiance</div>
  <div class="footer-links">
    <a href="#">Mentions légales</a>
    <a href="#">Politique de confidentialité</a>
    <a href="#">Accessibilité</a>
    <a href="#">Recrutement</a>
    <a href="#">CGU</a>
  </div>
  <div class="footer-copy">© 2026 Umbrella Assurance — Tous droits réservés · Société soumise au contrôle de l'ACPR</div>
</div>
""", unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([10, 3, 10])
with col_m:
    if st.button("✉️ Contact", type="secondary", use_container_width=False, key="btn_contact"):
        st.session_state.easter_open = True


@st.dialog("L'équipe Umbrella 🛡️")
def show_easter_egg():
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1.2rem;">
        <div style="
            display:inline-block;
            background:#c8a84b;
            color:#0d1b2a;
            font-weight:700;
            font-size:0.72rem;
            padding:4px 14px;
            border-radius:20px;
            letter-spacing:2px;
            text-transform:uppercase;
            margin-bottom:0.8rem;
        ">🥚 EASTER EGG DÉCOUVERT !</div>
        <h3 style="
            font-family:'Raleway',sans-serif;
            font-weight:800;
            color:#0d1b2a;
            font-size:1.3rem;
            margin-bottom:0.3rem;
        ">L'équipe derrière Umbrella</h3>
        <p style="color:#64748b; font-size:0.87rem;">
            Les cerveaux qui ont tout construit 🧠💻
        </p>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists("assets/Nous.jpg"):
        st.image("assets/Nous.jpg", use_container_width=True)
    else:
        st.warning("⚠️ Photo introuvable — placez Nous.jpg dans le dossier assets/")


if st.session_state.easter_open:
    show_easter_egg()
    st.session_state.easter_open = False
