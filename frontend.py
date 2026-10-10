import html
import random
from datetime import datetime
from math import cos, pi, sin
import os
import requests
import streamlit as st

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="Airline Satisfaction Predictor",
    page_icon="✈️",
    layout="wide",
)

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/predict"
)
API_BASE = API_URL.rsplit("/", 1)[0]

# ---------------- Data definitions ----------------
# (API field name, widget key, short radar label, default rating)
RATING_FEATURES = [
    ("Inflight wifi service", "r_wifi", "Wifi", 4),
    ("Departure/Arrival time convenient", "r_time", "Timing", 3),
    ("Ease of Online booking", "r_booking", "Booking", 4),
    ("Gate location", "r_gate", "Gate", 3),
    ("Food and drink", "r_food", "Food", 4),
    ("Online boarding", "r_boarding", "Boarding", 5),
    ("Seat comfort", "r_seat", "Seat", 4),
    ("Inflight entertainment", "r_entertain", "Screen", 4),
    ("On-board service", "r_service", "Service", 4),
    ("Leg room service", "r_legroom", "Legroom", 4),
    ("Baggage handling", "r_baggage", "Baggage", 4),
    ("Checkin service", "r_checkin", "Check-in", 4),
    ("Cleanliness", "r_clean", "Clean", 4),
]
KEY_OF = {name: key for name, key, _, _ in RATING_FEATURES}

RATING_GROUPS = [
    (
        "🧳 Booking and airport",
        [
            "Ease of Online booking",
            "Departure/Arrival time convenient",
            "Online boarding",
            "Checkin service",
            "Gate location",
            "Baggage handling",
        ],
    ),
    (
        "💺 In the cabin",
        [
            "Seat comfort",
            "Leg room service",
            "Cleanliness",
            "Food and drink",
            "Inflight entertainment",
            "Inflight wifi service",
            "On-board service",
        ],
    ),
]

FACES = ["😡", "😞", "😕", "😐", "🙂", "🤩"]

DEFAULT_STATE = {
    "age": 28,
    "gender": "Male",
    "customer_type": "Loyal Customer",
    "travel_type": "Business travel",
    "travel_class": "Business",
    "distance": 1500,
    "dep_delay": 0.0,
    "arr_delay": 0.0,
    **{key: default for _, key, _, default in RATING_FEATURES},
}


def ratings_of(value, **override):
    state = {key: value for _, key, _, _ in RATING_FEATURES}
    state.update(override)
    return state


PRESETS = {
    "happy": {
        "age": 41,
        "gender": "Female",
        "customer_type": "Loyal Customer",
        "travel_type": "Business travel",
        "travel_class": "Business",
        "distance": 2800,
        "dep_delay": 0.0,
        "arr_delay": 0.0,
        **ratings_of(5, r_wifi=4, r_gate=4, r_time=4),
    },
    "budget": {
        "age": 24,
        "gender": "Male",
        "customer_type": "disloyal Customer",
        "travel_type": "Personal Travel",
        "travel_class": "Eco",
        "distance": 650,
        "dep_delay": 10.0,
        "arr_delay": 5.0,
        **ratings_of(3, r_wifi=2, r_entertain=3),
    },
    "delayed": {
        "age": 35,
        "gender": "Male",
        "customer_type": "Loyal Customer",
        "travel_type": "Business travel",
        "travel_class": "Eco Plus",
        "distance": 1200,
        "dep_delay": 130.0,
        "arr_delay": 145.0,
        **ratings_of(2, r_service=1, r_baggage=1, r_checkin=2),
    },
    "reset": DEFAULT_STATE,
}


# ---------------- State and callbacks ----------------
for _k, _v in DEFAULT_STATE.items():
    st.session_state.setdefault(_k, _v)
st.session_state.setdefault("result", None)
st.session_state.setdefault("history", [])


def apply_preset(name):
    for k, v in PRESETS[name].items():
        st.session_state[k] = v


def randomize_ratings():
    for _, key, _, _ in RATING_FEATURES:
        st.session_state[key] = random.randint(1, 5)


def clear_history():
    st.session_state.history = []


@st.cache_data(ttl=5, show_spinner=False)
def backend_online(url):
    try:
        requests.get(url, timeout=1.5)
        return True
    except requests.exceptions.RequestException:
        return False


# ---------------- Custom Styling ----------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap');

:root {
    --ink: #0b1f3a;
    --muted: #5b6b82;
    --sky: #eaf1f8;
    --card: #ffffff;
    --accent: #ff6a3d;
    --good: #12936b;
    --warn: #d9534f;
    --line: #d5e0ec;
}

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}
.stApp {
    background: linear-gradient(180deg, #dbe9f7 0, var(--sky) 380px, var(--sky) 100%);
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1180px; }

/* Hero */
.hero {
    background: linear-gradient(120deg, #0b1f3a 0%, #17406f 60%, #2a6db0 100%);
    border-radius: 22px;
    padding: 38px 44px;
    color: #fff;
    position: relative;
    overflow: hidden;
    margin-bottom: 18px;
}
.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1.1;
    margin: 0 0 10px 0;
    color: #fff;
    letter-spacing: -0.5px;
    max-width: 640px;
}
.hero p { margin: 0 0 18px 0; color: #c8d9ee; font-size: 1.05rem; max-width: 520px; }
.hero .trail {
    position: absolute; right: 0; bottom: 0; width: 55%; height: 100%;
    opacity: .9; pointer-events: none;
}
.hero .plane {
    position: absolute; right: 42px; top: 26px;
    font-size: 5.5rem; transform: rotate(-12deg);
    animation: drift 6s ease-in-out infinite;
}
@keyframes drift {
    0%, 100% { transform: rotate(-12deg) translateY(0); }
    50% { transform: rotate(-8deg) translateY(-10px); }
}
.status {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 5px 14px; border-radius: 99px; font-size: .85rem; font-weight: 500;
    background: rgba(255, 255, 255, .12); color: #fff;
}
.status i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.status.on i { background: #4ade80; box-shadow: 0 0 0 4px rgba(74, 222, 128, .25); }
.status.off i { background: #fb7185; box-shadow: 0 0 0 4px rgba(251, 113, 133, .25); }

/* Section headings */
.sec {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    margin: 6px 0 2px 0;
}
.sec-sub { color: var(--muted); font-size: .92rem; margin-bottom: 10px; }

/* Bordered containers become cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 20px rgba(11, 31, 58, .06);
    padding: 6px 10px;
}

/* Inputs */
label, .stSlider label p, .stSelectbox label p, .stNumberInput label p, .stRadio label p {
    font-weight: 500 !important;
    color: var(--ink) !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--accent) !important;
    box-shadow: none !important;
}
.stSlider [data-testid="stThumbValue"] { color: var(--accent) !important; font-weight: 700; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { font-weight: 700; padding: 8px 14px; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--accent) !important; }

/* Buttons */
.stButton > button p { color: inherit !important; font-weight: inherit; }
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    width: 100%;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 14px;
    height: 3.4em;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    transition: transform .15s ease, box-shadow .15s ease;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    background: #ee5a2d; color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(255, 106, 61, .35);
}
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background: #fff;
    color: var(--ink);
    border: 1px solid var(--line);
    border-radius: 99px;
    font-weight: 500;
    font-size: .9rem;
    transition: border-color .15s ease, color .15s ease;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--accent); color: var(--accent);
}
.stButton > button:focus-visible { outline: 3px solid #0b1f3a; outline-offset: 2px; }

/* Live service profile */
.radar { width: 100%; height: auto; display: block; }
.radar .ring { fill: none; stroke: var(--line); stroke-width: 1; }
.radar .ring.top { stroke: #b9c9dc; }
.radar .spoke { stroke: var(--line); stroke-width: 1; }
.radar .shape { fill: rgba(255, 106, 61, .22); stroke: var(--accent); stroke-width: 2.5; stroke-linejoin: round; }
.radar .dot { fill: var(--accent); }
.radar text { font-family: 'DM Sans', sans-serif; font-size: 11.5px; fill: var(--muted); }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 4px 0 10px 0; }
.stat { background: #f3f7fb; border-radius: 12px; padding: 10px 12px; }
.stat b { display: block; font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.25rem; }
.stat span { color: var(--muted); font-size: .8rem; }

/* Boarding-pass result */
.ticket {
    position: relative;
    background: #fff;
    border-radius: 20px;
    border: 1px solid var(--line);
    box-shadow: 0 14px 34px rgba(11, 31, 58, .12);
    margin-top: 14px;
    overflow: hidden;
    transition: opacity .25s ease, filter .25s ease;
}
.ticket.stale { opacity: .55; filter: grayscale(.6); }
.ticket-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 22px 24px 14px 24px; }
.t-label { color: var(--muted); font-size: .85rem; }
.t-verdict { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.9rem; line-height: 1.1; margin: 2px 0 6px 0; }
.t-sub { color: var(--muted); font-size: .92rem; }
.ticket.ok .t-verdict { color: var(--good); }
.ticket.bad .t-verdict { color: var(--warn); }
.ring-svg { width: 124px; height: 124px; flex: none; }
.ring-bg { fill: none; stroke: #e6edf5; stroke-width: 12; }
.ring-fg {
    fill: none; stroke-width: 12; stroke-linecap: round;
    stroke-dasharray: 364.42;
    animation: sweep 1.1s cubic-bezier(.2, .7, .2, 1) both;
}
.ticket.ok .ring-fg { stroke: var(--good); }
.ticket.bad .ring-fg { stroke: var(--warn); }
@keyframes sweep { from { stroke-dashoffset: 364.42; } }
.ring-num { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 26px; fill: var(--ink); }
.perf { position: relative; height: 22px; }
.perf .rule { position: absolute; left: 18px; right: 18px; top: 10px; border-top: 2px dashed var(--line); }
.perf .notch { position: absolute; top: 0; width: 22px; height: 22px; border-radius: 50%; background: var(--sky); border: 1px solid var(--line); }
.perf .notch.l { left: -12px; }
.perf .notch.r { right: -12px; }
.ticket-bot { padding: 8px 24px 20px 24px; }
.group-label { color: var(--muted); font-size: .85rem; margin: 8px 0 6px 0; }
.chip {
    display: inline-block; padding: 4px 11px; margin: 0 6px 6px 0;
    border-radius: 99px; font-size: .85rem; font-weight: 500;
}
.chip.good { background: #e3f6ef; color: #0b6e50; }
.chip.low { background: #fde8e7; color: #a93a37; }
.stale-badge {
    position: absolute; top: 12px; right: 14px;
    background: var(--ink); color: #fff; font-size: .8rem; font-weight: 500;
    padding: 4px 12px; border-radius: 99px;
}

/* History */
.hist { display: flex; align-items: center; gap: 10px; padding: 8px 2px; border-bottom: 1px solid var(--line); font-size: .92rem; }
.hist:last-child { border-bottom: none; }
.hist i { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.hist i.ok { background: var(--good); }
.hist i.bad { background: var(--warn); }
.hist .when { margin-left: auto; color: var(--muted); font-size: .82rem; }

@media (prefers-reduced-motion: reduce) {
    .hero .plane, .ring-fg { animation: none; }
}
@media (max-width: 700px) {
    .hero { padding: 26px; }
    .hero h1 { font-size: 1.8rem; }
    .hero .plane { font-size: 3.5rem; right: 18px; }
    .stats { grid-template-columns: 1fr; }
    .ticket-top { flex-direction: column-reverse; align-items: flex-start; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- Hero ----------------
online = backend_online(API_BASE)
status_html = (
    '<span class="status on"><i></i>Prediction service online</span>'
    if online
    else '<span class="status off"><i></i>Prediction service offline</span>'
)
st.markdown(
    '<div class="hero">'
    '<svg class="trail" viewBox="0 0 400 200" preserveAspectRatio="none">'
    '<path d="M0 190 C 90 190, 130 70, 230 90 S 350 40, 400 20" fill="none" '
    'stroke="rgba(255,255,255,.35)" stroke-width="2" stroke-dasharray="6 9"/></svg>'
    '<div class="plane">✈️</div>'
    "<h1>Will this passenger be happy with the flight?</h1>"
    "<p>Set the trip details and rate each service. The model predicts whether the passenger will be satisfied.</p>"
    f"{status_html}"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------- Quick scenarios ----------------
st.markdown('<div class="sec">Start from a scenario</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-sub">Load a ready-made passenger, then adjust anything you like.</div>',
    unsafe_allow_html=True,
)
p1, p2, p3, p4, p5 = st.columns(5)
with p1:
    st.button("😊 Happy flyer", key="b_happy", on_click=apply_preset, args=("happy",), use_container_width=True)
with p2:
    st.button("🎒 Budget trip", key="b_budget", on_click=apply_preset, args=("budget",), use_container_width=True)
with p3:
    st.button("😤 Long delay", key="b_delayed", on_click=apply_preset, args=("delayed",), use_container_width=True)
with p4:
    st.button("🎲 Random ratings", key="b_random", on_click=randomize_ratings, use_container_width=True)
with p5:
    st.button("↺ Reset", key="b_reset", on_click=apply_preset, args=("reset",), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.5, 1], gap="large")

# ---------------- Left: inputs ----------------
with left:
    st.markdown('<div class="sec">Passenger and trip</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Who is flying and what the journey looked like.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Age", min_value=0, max_value=100, key="age")
            st.radio("Gender", ["Male", "Female"], horizontal=True, key="gender")
            st.radio(
                "Customer type",
                ["Loyal Customer", "disloyal Customer"],
                horizontal=True,
                key="customer_type",
            )
        with c2:
            st.radio(
                "Type of travel",
                ["Business travel", "Personal Travel"],
                horizontal=True,
                key="travel_type",
            )
            st.radio("Class", ["Business", "Eco", "Eco Plus"], horizontal=True, key="travel_class")
            st.slider("Flight distance", min_value=0, max_value=6000, step=50, key="distance")

        d1, d2 = st.columns(2)
        with d1:
            st.number_input("Departure delay (minutes)", min_value=0.0, step=5.0, key="dep_delay")
        with d2:
            st.number_input("Arrival delay (minutes)", min_value=0.0, step=5.0, key="arr_delay")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Service ratings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sec-sub">Slide each service from 0 (lowest) to 5 (highest). The profile on the right updates as you go.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        tabs = st.tabs([title for title, _ in RATING_GROUPS])
        for tab, (_, names) in zip(tabs, RATING_GROUPS):
            with tab:
                cols = st.columns(2)
                for i, name in enumerate(names):
                    with cols[i % 2]:
                        st.select_slider(
                            name,
                            options=[0, 1, 2, 3, 4, 5],
                            format_func=lambda v: f"{FACES[v]} {v}",
                            key=KEY_OF[name],
                        )

# ---------------- Collect current values ----------------
ratings = {name: st.session_state[key] for name, key, _, _ in RATING_FEATURES}

payload = {
    "Age": st.session_state.age,
    "Gender": st.session_state.gender,
    "Customer Type": st.session_state.customer_type,
    "Type of Travel": st.session_state.travel_type,
    "Class": st.session_state.travel_class,
    "Flight Distance": st.session_state.distance,
    "Inflight wifi service": ratings["Inflight wifi service"],
    "Departure/Arrival time convenient": ratings["Departure/Arrival time convenient"],
    "Ease of Online booking": ratings["Ease of Online booking"],
    "Gate location": ratings["Gate location"],
    "Food and drink": ratings["Food and drink"],
    "Online boarding": ratings["Online boarding"],
    "Seat comfort": ratings["Seat comfort"],
    "Inflight entertainment": ratings["Inflight entertainment"],
    "On-board service": ratings["On-board service"],
    "Leg room service": ratings["Leg room service"],
    "Baggage handling": ratings["Baggage handling"],
    "Checkin service": ratings["Checkin service"],
    "Cleanliness": ratings["Cleanliness"],
    "Departure Delay in Minutes": st.session_state.dep_delay,
    "Arrival Delay in Minutes": st.session_state.arr_delay,
}


# ---------------- Rendering helpers ----------------
def radar_svg(values, labels):
    cx, cy, radius, label_radius = 200, 185, 105, 130
    n = len(values)

    def point(i, r):
        angle = -pi / 2 + 2 * pi * i / n
        return cx + r * cos(angle), cy + r * sin(angle), cos(angle)

    parts = []
    for level in range(1, 6):
        pts = " ".join(f"{point(i, radius * level / 5)[0]:.1f},{point(i, radius * level / 5)[1]:.1f}" for i in range(n))
        parts.append(f'<polygon points="{pts}" class="ring{" top" if level == 5 else ""}"/>')
    for i in range(n):
        x, y, _ = point(i, radius)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" class="spoke"/>')

    shape = [point(i, radius * v / 5) for i, v in enumerate(values)]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in shape)
    parts.append(f'<polygon points="{pts}" class="shape"/>')
    for x, y, _ in shape:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="dot"/>')

    for i, label in enumerate(labels):
        x, y, c = point(i, label_radius)
        anchor = "middle" if abs(c) < 0.3 else ("start" if c > 0 else "end")
        parts.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}">{html.escape(label)}</text>')

    return (
        '<svg viewBox="0 0 400 370" class="radar" role="img" '
        'aria-label="Radar chart of the 13 service ratings">' + "".join(parts) + "</svg>"
    )


def result_html(res, stale):
    prediction = res["prediction"]
    probability = max(0.0, min(1.0, float(res["probability"])))
    pct = probability * 100
    satisfied = prediction == "Satisfied"
    css = "ok" if satisfied else "bad"
    verdict = "Satisfied" if satisfied else html.escape(str(prediction))
    sub = "Likely a happy passenger" if satisfied else "Likely to leave unhappy"
    offset = 364.42 * (1 - probability)

    ring = (
        '<svg viewBox="0 0 140 140" class="ring-svg" role="img" '
        f'aria-label="{pct:.1f} percent chance of satisfaction">'
        '<circle cx="70" cy="70" r="58" class="ring-bg"/>'
        f'<circle cx="70" cy="70" r="58" class="ring-fg" transform="rotate(-90 70 70)" '
        f'style="stroke-dashoffset:{offset:.2f}"/>'
        f'<text x="70" y="78" text-anchor="middle" class="ring-num">{pct:.1f}%</text></svg>'
    )

    snap = res["payload"]
    scored = sorted(((n, snap[n]) for n, _, _, _ in RATING_FEATURES), key=lambda t: t[1])
    weak = [t for t in scored if t[1] <= 3][:3]
    strong = [t for t in reversed(scored) if t[1] >= 4][:3]

    insights = ""
    if strong:
        chips = "".join(f'<span class="chip good">{html.escape(n)} {v}</span>' for n, v in strong)
        insights += f'<div class="group-label">Highest rated</div>{chips}'
    if weak:
        chips = "".join(f'<span class="chip low">{html.escape(n)} {v}</span>' for n, v in weak)
        insights += f'<div class="group-label">Lowest rated</div>{chips}'
    if not insights:
        insights = '<div class="group-label">Ratings are all in the middle of the scale.</div>'

    badge = '<div class="stale-badge">Inputs changed, predict again</div>' if stale else ""
    return (
        f'<div class="ticket {css}{" stale" if stale else ""}">{badge}'
        '<div class="ticket-top"><div>'
        '<div class="t-label">Prediction</div>'
        f'<div class="t-verdict">{verdict}</div>'
        f'<div class="t-sub">{sub}</div></div>{ring}</div>'
        '<div class="perf"><span class="notch l"></span><span class="rule"></span><span class="notch r"></span></div>'
        f'<div class="ticket-bot">{insights}</div></div>'
    )


# ---------------- Right: live profile, predict, result ----------------
with right:
    st.markdown('<div class="sec">Service profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">A live picture of the ratings you have set.</div>', unsafe_allow_html=True)

    values = [ratings[name] for name, _, _, _ in RATING_FEATURES]
    labels = [short for _, _, short, _ in RATING_FEATURES]
    average = sum(values) / len(values)
    weakest = min(RATING_FEATURES, key=lambda f: ratings[f[0]])
    total_delay = int(st.session_state.dep_delay + st.session_state.arr_delay)

    with st.container(border=True):
        st.markdown(
            radar_svg(values, labels)
            + '<div class="stats">'
            f'<div class="stat"><b>{average:.1f} / 5</b><span>Average rating</span></div>'
            f'<div class="stat"><b>{html.escape(weakest[2])}</b><span>Lowest area</span></div>'
            f'<div class="stat"><b>{total_delay} min</b><span>Total delay</span></div>'
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("Predict satisfaction ✈️", type="primary", use_container_width=True)

    if predict_clicked:
        try:
            with st.spinner("Checking the passenger's details..."):
                response = requests.post(API_URL, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                st.session_state.result = {
                    "prediction": data["prediction"],
                    "probability": data["probability"],
                    "payload": dict(payload),
                }
                pct_now = max(0.0, min(1.0, float(data["probability"]))) * 100
                st.session_state.history.append(
                    {
                        "ok": data["prediction"] == "Satisfied",
                        "label": "Satisfied" if data["prediction"] == "Satisfied" else str(data["prediction"]),
                        "pct": pct_now,
                        "cls": payload["Class"],
                        "time": datetime.now().strftime("%H:%M"),
                    }
                )
                st.toast("Prediction ready", icon="✅")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Can't reach the FastAPI backend at "
                f"{API_URL}. Start the backend and try again."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Request failed: {error}")

    if st.session_state.result:
        is_stale = st.session_state.result["payload"] != payload
        st.markdown(result_html(st.session_state.result, is_stale), unsafe_allow_html=True)

# ---------------- History ----------------
if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"Prediction history ({len(st.session_state.history)})"):
        rows = "".join(
            f'<div class="hist"><i class="{"ok" if h["ok"] else "bad"}"></i>'
            f'<b>{html.escape(h["label"])}</b> at {h["pct"]:.1f}%, {html.escape(h["cls"])} class'
            f'<span class="when">{h["time"]}</span></div>'
            for h in reversed(st.session_state.history[-8:])
        )
        st.markdown(rows, unsafe_allow_html=True)
        st.button("Clear history", key="b_clear", on_click=clear_history)