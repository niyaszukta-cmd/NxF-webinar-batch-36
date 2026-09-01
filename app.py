"""
Finzcom x NYZTrade - Webinar Library
====================================
A password-gated Streamlit app for sharing webinar recordings (Veed.io embeds).
Laid out for laptop and phone: the player resizes to the screen, and the session
list lives in the sidebar on desktop and in a collapsible picker on mobile.

Run locally:   streamlit run app.py
Set the password (in order of priority):
  1. .streamlit/secrets.toml  ->  APP_PASSWORD = "your-password"
  2. environment variable     ->  APP_PASSWORD=your-password
  3. the DEFAULT_PASSWORD constant below (change it before you deploy)
"""

import os
import re

import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# 1. ACCESS
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_PASSWORD = "hedgex2026"          # ← change this before sharing

# ─────────────────────────────────────────────────────────────────────────────
# 2. BRANDING / COPY
# ─────────────────────────────────────────────────────────────────────────────
BRAND_LEFT = "Finzcom"
BRAND_RIGHT = "NYZTrade"
SERIES_TITLE = "Gamma exposure, from first principles to live setups"
SERIES_BLURB = (
    "Seven recorded sessions on reading dealer positioning with GEX, VANNA and "
    "DEX — built around the HedGEX platform and the way Indian index options "
    "actually trade."
)
HOST_LINE = "Hosted by Dr. Niyas N · NYZTrade Financial Solutions"

# ─────────────────────────────────────────────────────────────────────────────
# 3. VIDEO LIBRARY
#    Add / remove / reorder entries freely.
#    embed: paste the full <iframe> embed code from Veed.io share → Embed.
#           Use a single-quoted Python string; the iframe src uses double quotes.
# ─────────────────────────────────────────────────────────────────────────────
HEDGEX_VIDEOS = [
    {
        "title": "Introduction",
        "desc": "Prelude",
        "thumbnail": "",
        "topics": [
            "General discussion on HedGEX and why we need this",
        ],
        "embed": '<iframe src="https://veed.io/embed/681df571-f6aa-4bd4-8fe2-7309c04cb3ee?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="The Prelude" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "Basics of options and hedging",
        "desc": "Deep dive into the basics of options",
        "thumbnail": "",
        "topics": [
            "What is an option?",
            "Why option trading?",
            "How market makers trade options",
            "Options from the buyer's and the seller's side",
            "Every chapter is practice-oriented",
        ],
        "embed": '<iframe src="https://veed.io/embed/f0394d7c-d4be-4ad1-8d0a-7b36e2982389?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="Basics of Options and Hedging" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "Option moneyness",
        "desc": "Picking strikes: ATM, ITM and OTM in depth",
        "thumbnail": "",
        "topics": [
            "What is ATM, and when to choose it",
            "What is ITM, and when to choose it",
            "What is OTM, and when to choose it",
            "Strike selection using GEX",
            "Every chapter is practice-oriented",
        ],
        "embed": '<iframe src="https://veed.io/embed/c05fa625-30c1-4d46-8115-6b924df873a9?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="Option Moneyness (Practical on ATM ITM OTM)" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "Option Greeks (first order)",
        "desc": "The Greeks in plain language",
        "thumbnail": "",
        "topics": [
            "Practical insights on delta",
            "Practical insights on gamma",
            "Practical insights on theta",
            "How the Greeks move option pricing (Black–Scholes)",
            "Reading the probability of profit from the Greeks",
            "Practical focus throughout, in everyday language",
        ],
        "embed": '<iframe src="https://veed.io/embed/da16724d-fe2a-4e54-938a-c345e36f63de?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="Option Greeks (practical on GAMMA , DELTA..etc)" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "Introduction to the HedGEX platform",
        "desc": "A tour of the dashboard",
        "thumbnail": "",
        "topics": [
            "Basic usage guidelines for the HedGEX option analytics platform",
        ],
        "embed": '<iframe src="https://veed.io/embed/347f70f6-8064-4261-b441-a8ecce5ffeb5?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="Introduction to HedGEX dashboard" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "Advanced GEX, VANNA and cascade analytics",
        "desc": "Trading options off GEX, VANNA and cascade reads",
        "thumbnail": "",
        "topics": [
            "Gamma exposure basics — call gamma wall, put gamma wall",
            "GEX for option sellers",
            "GEX for option buyers",
            "Reading dealer flow through GEX",
            "Marking dealer flow with GEX support and resistance (sellers' iron condor)",
            "Strike selection with GEX and enhanced GEX (unwinding)",
        ],
        "embed": '<iframe src="https://www.veed.io/embed/bfb639b1-62ed-4174-9118-d95ad7c1979b?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="Advanced GEX, VANNA and Cascade analytics" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
    {
        "title": "GEX formations masterclass",
        "desc": "Intraday and BTST setups — the core session",
        "thumbnail": "",
        "topics": [
            "GEX formation basics: the 9:20 rule for intraday, the 3:20 rule for BTST",
            "Bull ramps and bear ramps",
            "Sellers' condors",
            "Continuous bull ramps and continuous bear ramps",
            "GEX void / GEX brackets for marking support and resistance",
            "Gamma blast setups",
        ],
        "embed": '<iframe src="https://www.veed.io/embed/20a94300-8c67-4c08-9af2-a406de91a61e?watermark=0&color=&sharing=0&title=1" width="744" height="504" frameborder="0" title="GEX formations masterclass for Intraday and BTST options" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>',
    },
]

# Strike ladder behind the landing-page graphic: (strike, net gamma).
GEX_PROFILE = [
    (25400, 16), (25350, 30), (25300, 72), (25250, 54), (25200, 120),
    (25150, 88), (25100, 42), (25050, 64), (25000, 26), (24950, -18),
    (24900, -30), (24850, -52), (24800, -38),
]
# Shorter ladder for phones — same story, still readable at 360px.
GEX_PROFILE_SMALL = [
    (25300, 72), (25200, 120), (25100, 42), (25050, 64),
    (25000, 26), (24900, -30), (24850, -52),
]

VIDEO_RATIO = 504 / 744          # aspect ratio of the Veed embeds
PLAYER_MAX_H = 620               # px — cap on laptops so the page still scrolls

# ─────────────────────────────────────────────────────────────────────────────
# 4. PAGE SETUP
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{BRAND_LEFT} × {BRAND_RIGHT} — Webinar Library",
    page_icon="◧",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root{
  --ground:#0d2430;
  --panel:#123040;
  --line:rgba(242,233,220,.16);
  --ink:#f2e9dc;
  --ink-soft:#a9bfc9;
  --call:#e8a33d;
  --put:#d9635a;
}

.stApp{
  background:
    radial-gradient(120% 90% at 82% -10%, #1a4356 0%, rgba(26,67,86,0) 58%),
    var(--ground);
  color:var(--ink);
  font-family:'IBM Plex Sans',system-ui,sans-serif;
  -webkit-text-size-adjust:100%;
}
.block-container{
  padding-top:2.4rem;padding-bottom:4rem;max-width:1180px;
  padding-left:max(1.1rem,env(safe-area-inset-left));
  padding-right:max(1.1rem,env(safe-area-inset-right));
}

h1,h2,h3{font-family:'Bricolage Grotesque','IBM Plex Sans',sans-serif;color:var(--ink);}
p,li,label,span{color:var(--ink);}

/* ── wordmark ─────────────────────────────────────────────── */
.wordmark{
  font-family:'Bricolage Grotesque',sans-serif;font-weight:800;
  font-size:.95rem;letter-spacing:.02em;color:var(--ink);
}
.wordmark .x{color:var(--call);font-weight:500;padding:0 .35rem;}

/* ── landing ──────────────────────────────────────────────── */
.hero-title{
  font-size:clamp(1.85rem,4.4vw,3.35rem);line-height:1.06;font-weight:700;
  letter-spacing:-.02em;margin:.9rem 0 1rem;max-width:16ch;
}
.hero-blurb{
  color:var(--ink-soft);font-size:clamp(.95rem,2.6vw,1.02rem);line-height:1.65;
  max-width:52ch;margin-bottom:1.5rem;
}
.host{
  color:var(--ink-soft);font-size:.84rem;line-height:1.5;
  border-top:1px solid var(--line);padding-top:.9rem;margin-top:1.9rem;
}

.gate{
  border:1px solid var(--line);border-radius:4px;background:rgba(18,48,64,.55);
  padding:1.3rem 1.3rem 1rem;margin-top:.4rem;
}
.gate-h{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.05rem;margin-bottom:.15rem;}
.gate-p{color:var(--ink-soft);font-size:.86rem;line-height:1.5;margin-bottom:.9rem;}

.contents{border-top:1px solid var(--line);margin-top:2.6rem;padding-top:1.5rem;}
.contents h3{font-size:1.05rem;margin:0 0 .8rem;}
.c-row{display:flex;gap:1rem;align-items:baseline;padding:.62rem 0;border-bottom:1px solid rgba(242,233,220,.07);}
.c-num{font-family:'IBM Plex Mono',monospace;color:var(--call);font-size:.8rem;min-width:2.1rem;}
.c-title{font-weight:600;font-size:.97rem;line-height:1.35;}
.c-desc{color:var(--ink-soft);font-size:.86rem;line-height:1.45;}

/* two versions of the gamma ladder — one per screen size */
.viz-wide{display:block;}
.viz-narrow{display:none;margin:.4rem 0 1.5rem;}

/* ── player page ──────────────────────────────────────────── */
.chapter-kicker{font-family:'IBM Plex Mono',monospace;color:var(--call);font-size:.8rem;margin-bottom:.5rem;}
.chapter-title{font-size:clamp(1.35rem,3.6vw,2.05rem);line-height:1.18;font-weight:700;letter-spacing:-.01em;margin:0 0 .4rem;}
.chapter-desc{color:var(--ink-soft);font-size:clamp(.92rem,2.5vw,1rem);margin-bottom:1.2rem;max-width:60ch;}

.covers{margin-top:1.8rem;border-top:1px solid var(--line);padding-top:1.2rem;}
.covers h4{font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;margin:0 0 .7rem;}
.covers ul{list-style:none;padding:0;margin:0;}
.covers li{
  position:relative;padding-left:1.25rem;margin-bottom:.55rem;
  font-size:clamp(.92rem,2.5vw,.95rem);line-height:1.55;max-width:72ch;
}
.covers li::before{
  content:"";position:absolute;left:0;top:.62em;width:.42rem;height:.42rem;
  background:var(--call);border-radius:1px;
}

/* ── sidebar (laptop) ─────────────────────────────────────── */
[data-testid="stSidebar"]{background:#0a1d27;border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebarUserContent"]{padding-top:1.4rem;}
.rail-label{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.92rem;margin:1.3rem 0 .55rem;}
.rail-meta{color:var(--ink-soft);font-size:.78rem;}
.rail-bar{height:3px;background:rgba(242,233,220,.14);border-radius:2px;margin:.5rem 0 .25rem;}
.rail-bar > div{height:3px;background:var(--call);border-radius:2px;}

/* mobile-only session picker, hidden on wide screens */
.st-key-mobile_nav{display:none;}

/* ── controls ─────────────────────────────────────────────── */
.stButton > button{
  font-family:'IBM Plex Sans',sans-serif;font-weight:500;font-size:.88rem;
  border-radius:3px;padding:.5rem .8rem;text-align:left;line-height:1.35;
  min-height:2.5rem;transition:background .12s ease,border-color .12s ease;
}
.stButton > button[kind="secondary"]{background:transparent;color:var(--ink-soft);border:1px solid transparent;}
.stButton > button[kind="secondary"]:hover{background:rgba(242,233,220,.06);color:var(--ink);}
.stButton > button[kind="primary"]{
  background:rgba(232,163,61,.14);color:var(--ink);
  border:1px solid rgba(232,163,61,.55);border-left:3px solid var(--call);
}
.stButton > button[kind="primary"]:hover{background:rgba(232,163,61,.2);}
.stButton > button:focus-visible{outline:2px solid var(--call);outline-offset:2px;}

.stTextInput > div > div > input{
  background:rgba(13,36,48,.9);color:var(--ink);border:1px solid var(--line);
  border-radius:3px;font-family:'IBM Plex Sans',sans-serif;font-size:1rem;
}
.stTextInput > div > div > input:focus{border-color:var(--call);box-shadow:none;}
[data-testid="stForm"]{border:0;padding:0;}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:4px;background:rgba(18,48,64,.4);}
[data-testid="stAlert"]{border-radius:3px;}
footer,#MainMenu{visibility:hidden;}

/* ── laptop and up ────────────────────────────────────────── */
@media (min-width:641px){
  [data-testid="stSidebar"]{min-width:288px;max-width:322px;}
}

/* ── phones ───────────────────────────────────────────────── */
@media (max-width:640px){
  .block-container{padding-top:1.3rem;padding-bottom:2.6rem;}
  .hero-title{max-width:100%;margin:.7rem 0 .8rem;}
  .hero-blurb{margin-bottom:1.1rem;}
  .viz-wide{display:none;}
  .viz-narrow{display:block;}
  .gate{padding:1.05rem 1rem .9rem;}
  .contents{margin-top:2rem;}
  .c-row{gap:.7rem;padding:.55rem 0;}
  .c-num{min-width:1.7rem;}
  .covers{margin-top:1.4rem;}
  .st-key-mobile_nav{display:block;margin-bottom:1.1rem;}
  .stButton > button{min-height:2.9rem;font-size:.92rem;}   /* thumb-sized taps */
  .host{margin-top:1.5rem;}
}

@media (prefers-reduced-motion:reduce){
  *{transition:none !important;animation:none !important;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def expected_password() -> str:
    """Password from secrets, then environment, then the constant above."""
    try:
        value = st.secrets["APP_PASSWORD"]
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get("APP_PASSWORD", DEFAULT_PASSWORD)


def wordmark() -> str:
    return f'<div class="wordmark">{BRAND_LEFT}<span class="x">×</span>{BRAND_RIGHT}</div>'


def gamma_profile_svg(compact: bool = False) -> str:
    """Net gamma by strike — the landing page's one bold element."""
    rows_data = GEX_PROFILE_SMALL if compact else GEX_PROFILE
    if compact:
        vb_w, bar_h, gap, top, axis, scale = 392, 20, 11, 16, 175, 1.15
        strike_fs, label_fs = 12, 12
    else:
        vb_w, bar_h, gap, top, axis, scale = 620, 16, 8, 18, 250, 2.2
        strike_fs, label_fs = 11, 11.5

    deepest_put = abs(min(v for _, v in rows_data))
    gutter = axis - deepest_put * scale - 22      # strike labels sit clear of the bars
    peak_call = max(rows_data, key=lambda r: r[1])
    peak_put = min(rows_data, key=lambda r: r[1])

    marks = []
    for i, (strike, gex) in enumerate(rows_data):
        y = top + i * (bar_h + gap)
        width = abs(gex) * scale
        x = axis if gex >= 0 else axis - width
        colour = "var(--call)" if gex >= 0 else "var(--put)"
        emphasis = ".95" if (strike, gex) in (peak_call, peak_put) else ".5"
        marks.append(
            f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{bar_h}" '
            f'fill="{colour}" opacity="{emphasis}" rx="1"/>'
            f'<text x="{gutter:.1f}" y="{y + bar_h * .74:.1f}" text-anchor="end" '
            f'font-family="IBM Plex Mono, monospace" font-size="{strike_fs}" '
            f'fill="#a9bfc9" opacity=".85">{strike}</text>'
        )
        if (strike, gex) == peak_call:
            marks.append(
                f'<text x="{x + width + 10:.1f}" y="{y + bar_h * .74:.1f}" '
                f'font-family="IBM Plex Sans, sans-serif" font-size="{label_fs}" '
                f'fill="#e8a33d">call wall</text>'
            )
        if (strike, gex) == peak_put:
            marks.append(
                f'<text x="{axis + 12}" y="{y + bar_h * .74:.1f}" '
                f'font-family="IBM Plex Sans, sans-serif" font-size="{label_fs}" '
                f'fill="#d9635a">put wall</text>'
            )

    height = top * 2 + len(rows_data) * (bar_h + gap)
    spot_i = next((i for i, (_, g) in enumerate(rows_data) if g < 0), len(rows_data))
    spot_y = top + spot_i * (bar_h + gap) - gap / 2
    return f"""
<svg viewBox="0 0 {vb_w} {height}" width="100%" role="img"
     aria-label="Net gamma exposure by strike: the call wall sits above spot, the put wall below.">
  <line x1="{axis}" y1="{top - 6}" x2="{axis}" y2="{height - top + 6}"
        stroke="rgba(242,233,220,.28)" stroke-width="1"/>
  <line x1="{max(gutter - 34, 4):.1f}" y1="{spot_y}" x2="{vb_w - 20}" y2="{spot_y}"
        stroke="rgba(242,233,220,.35)" stroke-width="1" stroke-dasharray="3 4"/>
  <text x="{vb_w - 20}" y="{spot_y - 6}" text-anchor="end"
        font-family="IBM Plex Mono, monospace" font-size="{strike_fs}" fill="#a9bfc9">spot</text>
  {''.join(marks)}
</svg>
"""


def player_html(embed_code: str) -> str:
    """
    Rebuild the pasted Veed iframe so it tracks the column width instead of the
    fixed 744x504, then resize the surrounding Streamlit frame to match. Result:
    edge-to-edge video on a phone, capped height on a laptop, no letterboxing.
    """
    match = re.search(r'src="([^"]+)"', embed_code)
    src = match.group(1) if match else ""
    if not src:
        return embed_code
    return f"""
<style>
  html,body{{margin:0;padding:0;background:transparent;overflow:hidden;}}
  .stage{{
    width:100%;aspect-ratio:744/504;max-height:100vh;
    border:1px solid rgba(242,233,220,.16);border-radius:4px;
    overflow:hidden;background:#0a1d27;
  }}
  .stage iframe{{width:100%;height:100%;border:0;display:block;}}
</style>
<div class="stage">
  <iframe src="{src}" allow="autoplay; fullscreen; picture-in-picture; encrypted-media"
          allowfullscreen title="Session recording"></iframe>
</div>
<script>
  (function(){{
    var frame = window.frameElement;
    function fit(){{
      if (!frame) return;
      var w = document.documentElement.clientWidth;
      var h = Math.min(Math.round(w * {VIDEO_RATIO}) + 2, {PLAYER_MAX_H});
      frame.style.height = h + 'px';
      frame.setAttribute('height', h);
      if (frame.parentElement) frame.parentElement.style.height = h + 'px';
    }}
    fit();
    window.addEventListener('resize', fit);
    window.addEventListener('orientationchange', fit);
    if (window.ResizeObserver) {{ new ResizeObserver(fit).observe(document.body); }}
  }})();
</script>
"""


def go_to(index: int) -> None:
    st.session_state.chapter = index


# ─────────────────────────────────────────────────────────────────────────────
# 6. LANDING PAGE
# ─────────────────────────────────────────────────────────────────────────────
def landing() -> None:
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown(wordmark(), unsafe_allow_html=True)
        st.markdown(f'<h1 class="hero-title">{SERIES_TITLE}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="hero-blurb">{SERIES_BLURB}</p>', unsafe_allow_html=True)
        # phone-sized ladder, sits between the blurb and the password box
        st.markdown(
            f'<div class="viz-narrow">{gamma_profile_svg(compact=True)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gate">'
            '<div class="gate-h">Enter your access password</div>'
            '<div class="gate-p">Shared with everyone who attended the live sessions. '
            'No account, no email — just the password.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form("gate", clear_on_submit=False):
            entry = st.text_input(
                "Access password", type="password",
                placeholder="Password", label_visibility="collapsed",
            )
            unlocked = st.form_submit_button(
                "Open the library", type="primary", use_container_width=True
            )

        if unlocked:
            if entry and entry.strip() == expected_password():
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("That password doesn't match. Check the message from the host and try again.")

        st.markdown(f'<div class="host">{HOST_LINE}</div>', unsafe_allow_html=True)

    with right:
        st.markdown(f'<div class="viz-wide">{gamma_profile_svg()}</div>', unsafe_allow_html=True)

    rows = "".join(
        f'<div class="c-row"><div class="c-num">{i + 1:02d}</div>'
        f'<div><div class="c-title">{v["title"]}</div>'
        f'<div class="c-desc">{v["desc"]}</div></div></div>'
        for i, v in enumerate(HEDGEX_VIDEOS)
    )
    st.markdown(
        f'<div class="contents"><h3>What\'s inside — {len(HEDGEX_VIDEOS)} sessions</h3>'
        f'{rows}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
def session_buttons(idx: int, key_prefix: str) -> None:
    for i, v in enumerate(HEDGEX_VIDEOS):
        st.button(
            f"{i + 1:02d}   {v['title']}",
            key=f"{key_prefix}_{i}",
            type="primary" if i == idx else "secondary",
            use_container_width=True,
            on_click=go_to,
            args=(i,),
        )


def library() -> None:
    total = len(HEDGEX_VIDEOS)
    idx = min(st.session_state.get("chapter", 0), total - 1)
    video = HEDGEX_VIDEOS[idx]
    pct = int((idx + 1) / total * 100)

    # laptop: persistent left rail
    with st.sidebar:
        st.markdown(wordmark(), unsafe_allow_html=True)
        st.markdown('<div class="rail-label">Sessions</div>', unsafe_allow_html=True)
        session_buttons(idx, "nav")
        st.markdown(
            f'<div class="rail-bar"><div style="width:{pct}%"></div></div>'
            f'<div class="rail-meta">Session {idx + 1} of {total}</div>'
            '<div style="height:1.1rem"></div>',
            unsafe_allow_html=True,
        )
        if st.button("Lock the library", key="lock", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # phone: the same list, collapsed into the page (CSS hides it on laptops)
    with st.container(key="mobile_nav"):
        with st.expander(f"Sessions · {idx + 1} of {total}", expanded=False):
            session_buttons(idx, "mnav")

    st.markdown(
        f'<div class="chapter-kicker">Session {idx + 1:02d} / {total:02d}</div>'
        f'<h1 class="chapter-title">{video["title"]}</h1>'
        f'<p class="chapter-desc">{video["desc"]}</p>',
        unsafe_allow_html=True,
    )

    components.html(player_html(video["embed"]), height=PLAYER_MAX_H, scrolling=False)

    prev_col, next_col = st.columns(2)
    with prev_col:
        st.button(
            "← Previous session", key="prev", disabled=idx == 0,
            use_container_width=True, on_click=go_to, args=(idx - 1,),
        )
    with next_col:
        st.button(
            "Next session →", key="next", disabled=idx == total - 1,
            use_container_width=True, on_click=go_to, args=(idx + 1,),
        )

    topics = [t.strip() for t in (video.get("topics") or []) if t.strip()]
    if topics:
        items = "".join(f"<li>{t}</li>" for t in topics)
        st.markdown(
            f'<div class="covers"><h4>What this session covers</h4><ul>{items}</ul></div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div class="host">{HOST_LINE}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8. ROUTER
# ─────────────────────────────────────────────────────────────────────────────
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("chapter", 0)

if st.session_state.authenticated:
    library()
else:
    landing()
