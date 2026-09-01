"""
Finzcom x NYZTrade - Equity Trading Webinar Library
===================================================
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
DEFAULT_PASSWORD = "finzcom2026"         # ← change this before sharing

# ─────────────────────────────────────────────────────────────────────────────
# 2. BRANDING / COPY   ── edit freely
# ─────────────────────────────────────────────────────────────────────────────
BRAND_LEFT = "Finzcom"
BRAND_RIGHT = "NYZTrade"
SERIES_TITLE = "A working method for trading Indian equities"
SERIES_BLURB = (
    "Recorded sessions on reading price and volume, building a watchlist, "
    "sizing a position and knowing where you're wrong — taught on real charts, "
    "for people who trade their own money."
)
HOST_LINE = "Hosted by Dr. Niyas N · NYZTrade Financial Solutions"

# ─────────────────────────────────────────────────────────────────────────────
# 3. SESSION LIBRARY
#    Replace the titles, descriptions and topics below with your actual
#    curriculum. Paste each recording's Veed embed into "embed" — use a
#    single-quoted Python string, since the iframe src uses double quotes.
#    A session with an empty "embed" shows a "recording coming soon" card,
#    so you can publish the outline before every video is uploaded.
# ─────────────────────────────────────────────────────────────────────────────
WEBINAR_SESSIONS = [
    {
        "title": "Introduction",
        "desc": "What this series covers and how to use it",
        "topics": [
            "Who this series is for, and what it will not teach",
            "How the sessions build on each other",
        ],
        "embed": "",
    },
    {
        "title": "How the equity market actually works",
        "desc": "Participants, order types and the mechanics behind a fill",
        "topics": [
            "Who is on the other side of your trade",
            "Market, limit and stop-loss orders — when each one hurts you",
            "Delivery versus intraday, and what changes in your risk",
            "Costs that quietly decide whether a strategy survives",
        ],
        "embed": "",
    },
    {
        "title": "Reading price structure",
        "desc": "Trends, ranges, and levels that hold",
        "topics": [
            "Higher highs, lower lows, and what a trend really requires",
            "Marking support and resistance without cluttering the chart",
            "Ranges, breakouts and failed breakouts",
            "Choosing a timeframe and staying on it",
        ],
        "embed": "",
    },
    {
        "title": "Volume and participation",
        "desc": "Confirming a move with the flow behind it",
        "topics": [
            "Volume at breakouts versus volume in a base",
            "Delivery percentage and what it tells you",
            "Market breadth as a filter on individual names",
        ],
        "embed": "",
    },
    {
        "title": "Entries, stops and position sizing",
        "desc": "Turning a view into a trade with defined risk",
        "topics": [
            "Where the stop belongs — and why the chart decides, not your capital",
            "Sizing from risk per trade instead of lot convenience",
            "Scaling in, scaling out, and when averaging down is a mistake",
            "Risk-reward that survives a losing streak",
        ],
        "embed": "",
    },
    {
        "title": "Screening and watchlists",
        "desc": "Finding candidates before the market opens",
        "topics": [
            "Building a screen you can run in ten minutes",
            "Fundamental filters worth keeping for a swing trade",
            "Keeping the watchlist short enough to actually watch",
        ],
        "embed": "",
    },
    {
        "title": "Trade review and journaling",
        "desc": "The habit that compounds faster than the strategy",
        "topics": [
            "What to record on every trade",
            "Separating a bad trade from a losing trade",
            "Reviewing weekly and monthly without rewriting history",
        ],
        "embed": "",
    },
]

# Price action behind the landing-page graphic: (open, high, low, close, volume).
# A base, then a breakout above the prior high on expanding volume.
PRICE_ACTION = [
    (100, 103, 99, 102, 40), (102, 104, 100, 101, 35), (101, 102, 98, 99, 42),
    (99, 101, 97, 100, 38), (100, 102, 99, 101, 30), (101, 104, 100, 104, 55),
    (104, 105, 102, 103, 45), (103, 104, 101, 102, 36), (102, 103, 100, 102, 28),
    (102, 105, 101, 105, 62), (105, 109, 104, 108, 88), (108, 111, 107, 110, 74),
    (110, 112, 108, 109, 50), (109, 113, 109, 112, 58),
]
BREAKOUT_INDEX = 10          # candle that clears the prior high
PRIOR_HIGH = 105             # the level being broken

VIDEO_RATIO = 504 / 744      # aspect ratio of the Veed embeds
PLAYER_MAX_H = 620           # px — cap on laptops so the page still scrolls

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
  --up:#e8a33d;
  --down:#d9635a;
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
.wordmark .x{color:var(--up);font-weight:500;padding:0 .35rem;}

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
.c-num{font-family:'IBM Plex Mono',monospace;color:var(--up);font-size:.8rem;min-width:2.1rem;}
.c-title{font-weight:600;font-size:.97rem;line-height:1.35;}
.c-desc{color:var(--ink-soft);font-size:.86rem;line-height:1.45;}

/* two versions of the chart — one per screen size */
.viz-wide{display:block;}
.viz-narrow{display:none;margin:.4rem 0 1.5rem;}

/* ── player page ──────────────────────────────────────────── */
.chapter-kicker{font-family:'IBM Plex Mono',monospace;color:var(--up);font-size:.8rem;margin-bottom:.5rem;}
.chapter-title{font-size:clamp(1.35rem,3.6vw,2.05rem);line-height:1.18;font-weight:700;letter-spacing:-.01em;margin:0 0 .4rem;}
.chapter-desc{color:var(--ink-soft);font-size:clamp(.92rem,2.5vw,1rem);margin-bottom:1.2rem;max-width:60ch;}

.pending{
  border:1px dashed var(--line);border-radius:4px;background:rgba(18,48,64,.35);
  padding:2.6rem 1.4rem;text-align:center;
}
.pending strong{font-family:'Bricolage Grotesque',sans-serif;font-size:1.02rem;display:block;margin-bottom:.35rem;}
.pending span{color:var(--ink-soft);font-size:.9rem;}

.covers{margin-top:1.8rem;border-top:1px solid var(--line);padding-top:1.2rem;}
.covers h4{font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;margin:0 0 .7rem;}
.covers ul{list-style:none;padding:0;margin:0;}
.covers li{
  position:relative;padding-left:1.25rem;margin-bottom:.55rem;
  font-size:clamp(.92rem,2.5vw,.95rem);line-height:1.55;max-width:72ch;
}
.covers li::before{
  content:"";position:absolute;left:0;top:.62em;width:.42rem;height:.42rem;
  background:var(--up);border-radius:1px;
}

/* ── sidebar (laptop) ─────────────────────────────────────── */
[data-testid="stSidebar"]{background:#0a1d27;border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebarUserContent"]{padding-top:1.4rem;}
.rail-label{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.92rem;margin:1.3rem 0 .55rem;}
.rail-meta{color:var(--ink-soft);font-size:.78rem;}
.rail-bar{height:3px;background:rgba(242,233,220,.14);border-radius:2px;margin:.5rem 0 .25rem;}
.rail-bar > div{height:3px;background:var(--up);border-radius:2px;}

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
  border:1px solid rgba(232,163,61,.55);border-left:3px solid var(--up);
}
.stButton > button[kind="primary"]:hover{background:rgba(232,163,61,.2);}
.stButton > button:focus-visible{outline:2px solid var(--up);outline-offset:2px;}

.stTextInput > div > div > input{
  background:rgba(13,36,48,.9);color:var(--ink);border:1px solid var(--line);
  border-radius:3px;font-family:'IBM Plex Sans',sans-serif;font-size:1rem;
}
.stTextInput > div > div > input:focus{border-color:var(--up);box-shadow:none;}
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
  .pending{padding:1.8rem 1rem;}
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


def price_chart_svg(compact: bool = False) -> str:
    """
    Candles and volume: a base, then a breakout through the prior high.
    The landing page's one bold element — and the thing the series is about.
    """
    if compact:
        candles = PRICE_ACTION[-8:]
        breakout = BREAKOUT_INDEX - (len(PRICE_ACTION) - 8)
        vb_w, pad_l, pad_r = 392, 20, 20
        price_top, price_h, vol_h, gap = 26, 168, 40, 16
        fs = 12
    else:
        candles = PRICE_ACTION
        breakout = BREAKOUT_INDEX
        vb_w, pad_l, pad_r = 620, 26, 26
        price_top, price_h, vol_h, gap = 24, 214, 52, 18
        fs = 11.5

    lo = min(c[2] for c in candles)
    hi = max(c[1] for c in candles)
    span = (hi - lo) or 1
    vol_top = price_top + price_h + gap
    height = vol_top + vol_h + 20
    slot = (vb_w - pad_l - pad_r) / len(candles)
    body_w = slot * 0.52
    max_vol = max(c[4] for c in candles)

    def y_of(price: float) -> float:
        return price_top + (hi - price) / span * price_h

    marks = []
    for i, (o, h, l, c, v) in enumerate(candles):
        cx = pad_l + slot * (i + 0.5)
        rising = c >= o
        colour = "var(--up)" if rising else "var(--down)"
        strong = i == breakout
        opacity = "1" if strong else ".62"
        top_y, bot_y = y_of(max(o, c)), y_of(min(o, c))
        marks.append(
            f'<line x1="{cx:.1f}" y1="{y_of(h):.1f}" x2="{cx:.1f}" y2="{y_of(l):.1f}" '
            f'stroke="{colour}" stroke-width="1.2" opacity="{opacity}"/>'
            f'<rect x="{cx - body_w / 2:.1f}" y="{top_y:.1f}" width="{body_w:.1f}" '
            f'height="{max(bot_y - top_y, 2):.1f}" fill="{colour}" opacity="{opacity}" rx="1"/>'
        )
        vh = v / max_vol * vol_h
        marks.append(
            f'<rect x="{cx - body_w / 2:.1f}" y="{vol_top + vol_h - vh:.1f}" '
            f'width="{body_w:.1f}" height="{vh:.1f}" fill="{colour}" '
            f'opacity="{".85" if strong else ".28"}" rx="1"/>'
        )

    level_y = y_of(PRIOR_HIGH)
    breakout_x = pad_l + slot * (breakout + 0.5)
    return f"""
<svg viewBox="0 0 {vb_w} {height}" width="100%" role="img"
     aria-label="A price chart: several sessions building a base, then a breakout above the prior high on rising volume.">
  <line x1="{pad_l}" y1="{level_y:.1f}" x2="{vb_w - pad_r}" y2="{level_y:.1f}"
        stroke="rgba(242,233,220,.4)" stroke-width="1" stroke-dasharray="3 4"/>
  <text x="{pad_l}" y="{level_y - 8:.1f}" font-family="IBM Plex Sans, sans-serif"
        font-size="{fs}" fill="#a9bfc9">prior high</text>
  <text x="{breakout_x:.1f}" y="{vol_top + vol_h + 15:.1f}" text-anchor="middle"
        font-family="IBM Plex Sans, sans-serif" font-size="{fs}" fill="#e8a33d">breakout on volume</text>
  <line x1="{pad_l}" y1="{vol_top + vol_h:.1f}" x2="{vb_w - pad_r}" y2="{vol_top + vol_h:.1f}"
        stroke="rgba(242,233,220,.18)" stroke-width="1"/>
  {''.join(marks)}
</svg>
"""


def player_html(src: str) -> str:
    """
    Rebuild the pasted Veed iframe so it tracks the column width instead of the
    fixed 744x504, then resize the surrounding Streamlit frame to match. Result:
    edge-to-edge video on a phone, capped height on a laptop, no letterboxing.
    """
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


def render_player(session: dict) -> None:
    """Play the recording, or show an honest empty state if none is set yet."""
    match = re.search(r'src="([^"]+)"', session.get("embed", "") or "")
    if match:
        components.html(player_html(match.group(1)), height=PLAYER_MAX_H, scrolling=False)
    else:
        st.markdown(
            '<div class="pending"><strong>Recording is not up yet</strong>'
            '<span>It will appear here as soon as the session is uploaded.</span></div>',
            unsafe_allow_html=True,
        )


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
        # phone-sized chart, sits between the blurb and the password box
        st.markdown(
            f'<div class="viz-narrow">{price_chart_svg(compact=True)}</div>',
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
        st.markdown(f'<div class="viz-wide">{price_chart_svg()}</div>', unsafe_allow_html=True)

    rows = "".join(
        f'<div class="c-row"><div class="c-num">{i + 1:02d}</div>'
        f'<div><div class="c-title">{s["title"]}</div>'
        f'<div class="c-desc">{s["desc"]}</div></div></div>'
        for i, s in enumerate(WEBINAR_SESSIONS)
    )
    st.markdown(
        f'<div class="contents"><h3>What\'s inside — {len(WEBINAR_SESSIONS)} sessions</h3>'
        f'{rows}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
def session_buttons(idx: int, key_prefix: str) -> None:
    for i, s in enumerate(WEBINAR_SESSIONS):
        st.button(
            f"{i + 1:02d}   {s['title']}",
            key=f"{key_prefix}_{i}",
            type="primary" if i == idx else "secondary",
            use_container_width=True,
            on_click=go_to,
            args=(i,),
        )


def library() -> None:
    total = len(WEBINAR_SESSIONS)
    idx = min(st.session_state.get("chapter", 0), total - 1)
    session = WEBINAR_SESSIONS[idx]
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
        f'<h1 class="chapter-title">{session["title"]}</h1>'
        f'<p class="chapter-desc">{session["desc"]}</p>',
        unsafe_allow_html=True,
    )

    render_player(session)

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

    topics = [t.strip() for t in (session.get("topics") or []) if t.strip()]
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
