
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json, os, hashlib, random, time, re
import streamlit.components.v1 as components 
from datetime import datetime, timedelta

def now_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def greeting():
    h = now_ist().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"

# ============================================================
# VALORMIND V2 - SIH PROTOTYPE
# ============================================================

st.set_page_config(
    page_title="VALORMIND",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "valormind_users.json"
HISTORY_FILE = "valormind_history.json"

# -------------------------
# STORAGE HELPERS
# -------------------------
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    users = load_json(DATA_FILE, {})
    if not users:
        users = {
            "person001": {
                "pin": hash_pin("1234"),
                "name": "Personnel 001",
                "role": "personnel"
            },
            "person002": {
                "pin": hash_pin("2345"),
                "name": "Personnel 002",
                "role": "personnel"
            }
        }
    return users

USERS = load_users()

ADMIN = {
    "welfare": {
        "pin": hash_pin("9999"),
        "name": "Welfare Officer",
        "role": "admin"
    }
}

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.stApp {
    background: #f6f8fb;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1250px;
}
.hero {
    padding: 34px;
    border-radius: 22px;
    background: linear-gradient(135deg,#0f172a,#1e3a5f);
    color: white;
    margin-bottom: 22px;
}
.hero h1 { font-size: 44px; margin: 0; }
.hero p { font-size: 17px; opacity: .88; }
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e6eaf0;
    box-shadow: 0 5px 18px rgba(15,23,42,.06);
    margin-bottom: 14px;
}
.welcome {
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
}
.muted { color:#64748b; }
.game-card {
    background:white;
    padding:22px;
    border-radius:18px;
    border:1px solid #e5e7eb;
    text-align:center;
    min-height:150px;
}
.risk-low {
    background:#dcfce7;color:#166534;padding:16px;border-radius:14px;font-weight:700;
}
.risk-medium {
    background:#fef3c7;color:#92400e;padding:16px;border-radius:14px;font-weight:700;
}
.risk-high {
    background:#fee2e2;color:#991b1b;padding:16px;border-radius:14px;font-weight:700;
}
.stButton>button { border-radius: 12px; font-weight: 600; }
.game-card { transition: transform .15s, box-shadow .15s; box-shadow: 0 5px 18px rgba(15,23,42,.06); margin-bottom: 8px; }
.game-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(15,23,42,.12); }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
defaults = {
    "logged_in": False,
    "role": None,
    "user": None,
    "page": "dashboard",
    "assessment_result": None,
    "checkin": None,
    "game": None,
    "reaction_started": False,
    "reaction_start": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------
# RISK ENGINE
# -------------------------
def calculate_risk(reaction_time, go_errors, memory_accuracy,
                   stroop_accuracy, attention_accuracy,
                   stress, fatigue, sleep):

    score = 0

    if reaction_time > 400:
        score += 20
    elif reaction_time > 350:
        score += 10

    if go_errors >= 6:
        score += 15
    elif go_errors >= 4:
        score += 8

    if memory_accuracy < 70:
        score += 15
    elif memory_accuracy < 80:
        score += 8

    if stroop_accuracy < 70:
        score += 15
    elif stroop_accuracy < 80:
        score += 8

    if attention_accuracy < 70:
        score += 15
    elif attention_accuracy < 80:
        score += 8

    if stress >= 8:
        score += 10
    elif stress >= 6:
        score += 5

    if fatigue >= 8:
        score += 10
    elif fatigue >= 6:
        score += 5

    if sleep < 5:
        score += 10
    elif sleep < 6:
        score += 5

    if score >= 55:
        risk = "HIGH"
    elif score >= 30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return risk, min(score, 100)

# -------------------------
# HISTORY
# -------------------------
def get_history(username):
    all_history = load_json(HISTORY_FILE, {})
    return all_history.get(username, [])

def save_result(username, result):
    all_history = load_json(HISTORY_FILE, {})
    all_history.setdefault(username, [])
    result["date"] = now_ist().strftime("%Y-%m-%d %H:%M")
    all_history[username].append(result)
    save_json(HISTORY_FILE, all_history)

# -------------------------
# LOGIN / SIGNUP
# -------------------------
def do_login(role, username):
    st.session_state.logged_in = True
    st.session_state.role = role
    st.session_state.user = username
    st.session_state.page = "dashboard"
    st.rerun()

def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

def login_page():
    st.markdown("""
    <div class="hero">
        <h1>🛡️ VALORMIND</h1>
        <p>Privacy-first Personnel Welfare & Cognitive Risk Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown("""
        <div class="card">
            <h3>Why VALORMIND?</h3>
            <p>🧠 Short cognitive checks<br>
            🎮 Relax & focus mini-games<br>
            📈 Personal trend, not judgement<br>
            🔒 Officers see summaries only</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("🔑 Demo credentials (for judges)"):
            st.code("Personnel:       person001 / 1234\nWelfare Officer: welfare / 9999")
        st.caption("Prototype uses voluntary/synthetic data. It does not diagnose medical or psychological conditions.")

    with right:
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab1:
            portal = st.radio("Choose portal", ["Personnel Portal", "Welfare Officer Portal"], horizontal=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="e.g. person001")
                pin = st.text_input("PIN", type="password", placeholder="4-6 digit PIN")
                submit = st.form_submit_button("Secure Sign In", type="primary", use_container_width=True)
            if submit:
                u = username.strip()
                u = u if (u in USERS or u in ADMIN) else u.lower()
                if portal == "Personnel Portal":
                    if u in USERS and USERS[u]["pin"] == hash_pin(pin):
                        do_login("personnel", u)
                    else:
                        st.error("Invalid username or PIN.")
                else:
                    if u in ADMIN and ADMIN[u]["pin"] == hash_pin(pin):
                        do_login("admin", u)
                    else:
                        st.error("Invalid Welfare Officer credentials.")

        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Choose username", placeholder="letters, numbers, _ (3-20)")
                new_name = st.text_input("Display name")
                new_pin = st.text_input("Create PIN", type="password", placeholder="4-6 digits")
                confirm_pin = st.text_input("Confirm PIN", type="password")
                submit2 = st.form_submit_button("Create Account & Sign In", type="primary", use_container_width=True)
            if submit2:
                u = new_user.strip().lower()
                if not re.fullmatch(r"[a-z0-9_]{3,20}", u):
                    st.error("Username: 3-20 characters, only letters, numbers and underscore.")
                elif u in USERS or u in ADMIN:
                    st.error("Username already exists.")
                elif not re.fullmatch(r"\d{4,6}", new_pin):
                    st.error("PIN must be 4-6 digits.")
                elif new_pin != confirm_pin:
                    st.error("PINs do not match.")
                else:
                    USERS[u] = {"pin": hash_pin(new_pin), "name": new_name.strip() or u, "role": "personnel"}
                    save_json(DATA_FILE, USERS)
                    do_login("personnel", u)

# -------------------------
# TOP NAV
# -------------------------
def top_nav():
    user = USERS.get(st.session_state.user, {})
    name = user.get("name", st.session_state.user)

    st.markdown(
        f'<div class="card"><b>🛡️ VALORMIND</b> &nbsp; | &nbsp; {name}</div>',
        unsafe_allow_html=True
    )

    if st.session_state.role == "personnel":
        cols = st.columns(5)
        labels = [
            ("🏠 Home", "dashboard"),
            ("🧠 Assessment", "assessment"),
            ("🎮 Relax & Focus", "games"),
            ("📈 My History", "history"),
            ("🚪 Logout", "logout")
        ]
        for c, (label, page) in zip(cols, labels):
            with c:
                if st.button(label, use_container_width=True, key=f"nav_{page}"):
                    if page == "logout":
                        logout()
                    else:
                        st.session_state.page = page
                        st.rerun()

# -------------------------
# PERSONNEL DASHBOARD
# -------------------------
def personnel_dashboard():
    top_nav()
    name = USERS[st.session_state.user]["name"]
    history = get_history(st.session_state.user)

    st.markdown(
        f'<div class="welcome">{greeting()}, {name} 👋</div>',
        unsafe_allow_html=True
    )
    st.caption("How are you doing today? VALORMIND helps you understand changes from your personal baseline.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧠 Start Cognitive Check", type="primary", use_container_width=True):
            st.session_state.page = "assessment"
            st.rerun()
    with c2:
        if st.button("🎮 Relax & Focus", use_container_width=True):
            st.session_state.page = "games"
            st.rerun()
    with c3:
        if st.button("📋 Quick Wellness Check-in", use_container_width=True):
            st.session_state.page = "checkin"
            st.rerun()

    st.markdown("---")

    latest = history[-1] if history else None
    if latest:
        risk = latest["risk"]
        cls = {"LOW":"risk-low", "MEDIUM":"risk-medium", "HIGH":"risk-high"}[risk]
        st.markdown(f'<div class="{cls}">Current indication: {risk} &nbsp; • &nbsp; Latest assessment: {latest["date"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No completed assessment yet. Start a short cognitive check to create your first personal baseline.")

    st.subheader("Your Personal Snapshot")
    a,b,c,d = st.columns(4)
    with a:
        st.metric("Assessments", len(history))
    with b:
        st.metric("Latest Risk", latest["risk"] if latest else "—")
    with c:
        st.metric("Reaction Time", f'{latest["reaction_time"]:.0f} ms' if latest else "—")
    with d:
        st.metric("Attention", f'{latest["attention_accuracy"]:.0f}%' if latest else "—")

    st.subheader("📈 Personal Trend")
    if history:
        vals = [x["score"] for x in history]
        dates = [x["date"] for x in history]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=vals, mode="lines+markers",
            name="Risk Index"
        ))
        fig.update_layout(
            height=320,
            template="plotly_white",
            yaxis_title="Risk Index",
            xaxis_title="Assessment"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Complete at least one assessment to start building your personal trend.")

    st.subheader("💡 Supportive Recommendation")
    if latest and latest["risk"] == "HIGH":
        st.warning("Several indicators are elevated. Consider recovery/support and, where appropriate, authorized human follow-up.")
    elif latest and latest["risk"] == "MEDIUM":
        st.info("Some indicators show deviation from your current pattern. Consider recovery and a follow-up assessment.")
    else:
        st.success("No significant concerning pattern is indicated in the latest prototype assessment.")

    st.caption("VALORMIND is a decision-support prototype. It does not diagnose medical or psychological conditions.")

# -------------------------
# WELLNESS CHECK-IN
# -------------------------
def checkin_page():
    top_nav()
    st.title("📝 Quick Wellness Check-in")
    st.write("A short voluntary check-in. Your responses are used as supporting indicators.")

    stress = st.slider("How stressed do you feel right now?", 0, 10, 4)
    fatigue = st.slider("How fatigued do you feel right now?", 0, 10, 4)
    sleep = st.slider("How many hours did you sleep last night?", 0.0, 12.0, 7.0, 0.5)
    mood = st.select_slider("Overall state", options=["Low","Okay","Good"], value="Okay")

    if st.button("Save Check-in", type="primary"):
        st.session_state.checkin = {
            "stress": stress, "fatigue": fatigue,
            "sleep": sleep, "mood": mood,
            "date": now_ist().strftime("%Y-%m-%d %H:%M")
        }
        st.success("Check-in saved for this session.")
        st.session_state.page = "dashboard"
        st.rerun()

# -------------------------
# COGNITIVE ASSESSMENT
# -------------------------
def assessment_page():
    top_nav()
    st.title("🧠 Quick Cognitive & Wellness Assessment")
    st.info("For the SIH prototype, these are short demonstrations. Results are interpreted as indicators, not diagnoses.")

    st.subheader("1. Reaction Time Challenge")
    st.write("Click the button after you see GO. For a simple Streamlit demo, the measured value is generated from your interaction.")

    if "reaction_value" not in st.session_state:
        st.session_state.reaction_value = None

    if st.button("🟢 GO!", type="primary"):
        st.session_state.reaction_value = random.randint(280, 460)

    reaction_time = st.session_state.reaction_value or 320
    if st.session_state.reaction_value:
        st.success(f"Recorded reaction time: {reaction_time} ms")

    st.subheader("2. Go / No-Go")
    go_errors = st.slider("Incorrect responses", 0, 15, 2)

    st.subheader("3. Working Memory — 2-Back")
    memory_accuracy = st.slider("Accuracy (%)", 0, 100, 85)

    st.subheader("4. Stroop Test")
    stroop_accuracy = st.slider("Accuracy (%)", 0, 100, 88)

    st.subheader("5. Sustained Attention")
    attention_accuracy = st.slider("Accuracy (%)", 0, 100, 90)

    st.subheader("6. Wellness")
    default_stress = st.session_state.checkin["stress"] if st.session_state.checkin else 4
    default_fatigue = st.session_state.checkin["fatigue"] if st.session_state.checkin else 4
    default_sleep = st.session_state.checkin["sleep"] if st.session_state.checkin else 7.0

    stress = st.slider("Perceived stress", 0, 10, default_stress)
    fatigue = st.slider("Fatigue", 0, 10, default_fatigue)
    sleep = st.slider("Sleep duration (hours)", 0.0, 12.0, default_sleep, 0.5)

    if st.button("Analyze My Results", type="primary", use_container_width=True):
        risk, score = calculate_risk(
            reaction_time, go_errors, memory_accuracy,
            stroop_accuracy, attention_accuracy,
            stress, fatigue, sleep
        )

        result = {
            "risk": risk,
            "score": score,
            "reaction_time": reaction_time,
            "go_errors": go_errors,
            "memory_accuracy": memory_accuracy,
            "stroop_accuracy": stroop_accuracy,
            "attention_accuracy": attention_accuracy,
            "stress": stress,
            "fatigue": fatigue,
            "sleep": sleep
        }

        save_result(st.session_state.user, result)
        st.session_state.assessment_result = result
        st.session_state.reaction_value = None
        st.session_state.page = "result"
        st.rerun()

# -------------------------
# RESULT
# -------------------------
def result_page():
    top_nav()
    result = st.session_state.get("assessment_result")
    if not result:
        st.warning("No assessment result available.")
        return

    st.title("Assessment Result")
    risk = result["risk"]

    if risk == "LOW":
        st.markdown('<div class="risk-low">🟢 LOW — No significant concerning pattern indicated</div>', unsafe_allow_html=True)
    elif risk == "MEDIUM":
        st.markdown('<div class="risk-medium">🟡 MEDIUM — Some indicators show meaningful deviation</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="risk-high">🔴 HIGH — Multiple indicators require authorized human review</div>', unsafe_allow_html=True)

    st.metric("Risk Index", f'{result["score"]}/100')

    st.subheader("🔎 Contributing Indicators")
    a,b,c = st.columns(3)
    with a:
        st.write("🧠 **Cognitive Performance**")
        st.write(f'Reaction: {result["reaction_time"]} ms')
        st.write(f'Memory: {result["memory_accuracy"]}%')
        st.write(f'Attention: {result["attention_accuracy"]}%')
    with b:
        st.write("😴 **Recovery**")
        st.write(f'Sleep: {result["sleep"]} h')
        st.write(f'Fatigue: {result["fatigue"]}/10')
    with c:
        st.write("📝 **Wellness**")
        st.write(f'Stress: {result["stress"]}/10')
        st.write(f'Stroop: {result["stroop_accuracy"]}%')

    if risk == "HIGH":
        st.warning("An authorized Welfare Officer should review the case before any intervention.")
    elif risk == "MEDIUM":
        st.info("Continue monitoring and consider appropriate recovery/support.")

    st.caption("Decision-support output only — not a medical diagnosis.")

# -------------------------
# HISTORY
# -------------------------
def history_page():
    top_nav()
    st.title("📈 My Assessment History")
    history = get_history(st.session_state.user)

    if not history:
        st.info("No assessment history yet.")
        return

    df = pd.DataFrame(history)
    st.dataframe(
        df[["date","risk","score","reaction_time","memory_accuracy","stroop_accuracy","attention_accuracy","stress","fatigue","sleep"]],
        use_container_width=True,
        hide_index=True
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["score"],
        mode="lines+markers",
        name="Risk Index"
    ))
    fig.update_layout(template="plotly_white", height=320)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# GAMES
# -------------------------
REACTION_HTML = """
<div style="font-family:sans-serif;text-align:center">
<div id="box" onclick="clickBox()" style="height:220px;border-radius:18px;background:#1e3a5f;color:white;display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer;user-select:none">Click to start</div>
<p id="res" style="font-size:18px;color:#0f172a"></p></div>
<script>
let state="idle",t0=0,timer=null,best=null;
const box=document.getElementById("box"),res=document.getElementById("res");
function clickBox(){
 if(state==="idle"){state="wait";box.style.background="#b91c1c";box.textContent="Wait for green...";
  timer=setTimeout(()=>{state="go";box.style.background="#16a34a";box.textContent="CLICK NOW!";t0=performance.now();},1000+Math.random()*2500);}
 else if(state==="wait"){clearTimeout(timer);state="idle";box.style.background="#1e3a5f";box.textContent="Too early! Click to retry";}
 else if(state==="go"){const ms=Math.round(performance.now()-t0);best=best===null?ms:Math.min(best,ms);state="idle";box.style.background="#1e3a5f";box.textContent=ms+" ms - click to play again";res.textContent="Last: "+ms+" ms | Best: "+best+" ms";}
}
</script>
"""

BREATH_HTML = """
<style>
.wrap{display:flex;flex-direction:column;align-items:center;font-family:sans-serif}
.c{width:120px;height:120px;border-radius:50%;background:radial-gradient(#93c5fd,#3b82f6);animation:b 12s ease-in-out infinite;margin:50px}
@keyframes b{0%{transform:scale(.6)}33%{transform:scale(1.5)}50%{transform:scale(1.5)}100%{transform:scale(.6)}}
</style>
<div class="wrap"><div class="c"></div><h3 id="t" style="color:#0f172a">Breathe in...</h3></div>
<script>
const t=document.getElementById("t");
const ph=[["Breathe in...",4000],["Hold...",2000],["Breathe out...",6000]];
let i=0;function s(){t.textContent=ph[i][0];setTimeout(()=>{i=(i+1)%3;s();},ph[i][1]);}s();
</script>
"""

STROOP_COLORS = {"RED": "#dc2626", "GREEN": "#16a34a", "BLUE": "#2563eb", "YELLOW": "#ca8a04"}

def add_points(n):
    st.session_state.points = st.session_state.get("points", 0) + n

def game_memory():
    ss = st.session_state
    ss.setdefault("mem_len", 3)
    ss.setdefault("mem_phase", "new")
    ss.setdefault("mem_best", 0)
    st.subheader("🧠 Memory Challenge")
    st.caption(f"Level {ss.mem_len - 2} • Best level: {ss.mem_best}")

    if ss.mem_phase == "new":
        msg = ss.pop("mem_msg", None)
        if msg:
            st.info(msg)
        if st.button("▶ Start round", type="primary"):
            ss.mem_seq = "".join(random.choice("ABCDEFGH") for _ in range(ss.mem_len))
            ss.mem_phase = "show"
            st.rerun()
    elif ss.mem_phase == "show":
        st.markdown(
            f'<div class="card" style="text-align:center;font-size:48px;letter-spacing:12px;font-weight:800">{ss.mem_seq}</div>',
            unsafe_allow_html=True)
        if st.button("I remember it → Hide", type="primary"):
            ss.mem_phase = "recall"
            st.rerun()
    else:
        with st.form("mem_form", clear_on_submit=True):
            guess = st.text_input("Type the sequence you saw")
            ok = st.form_submit_button("Check", type="primary")
        if ok:
            if guess.strip().upper() == ss.mem_seq:
                ss.mem_best = max(ss.mem_best, ss.mem_len - 2)
                ss.mem_len += 1
                add_points(10)
                ss.mem_msg = f"✅ Correct! Next round has {ss.mem_len} letters."
            else:
                ss.mem_msg = f"❌ Not quite. It was {ss.mem_seq}. Starting again."
                ss.mem_len = 3
            ss.mem_phase = "new"
            st.rerun()

def game_stroop():
    ss = st.session_state
    TOTAL = 8
    def new_item():
        return (random.choice(list(STROOP_COLORS)), random.choice(list(STROOP_COLORS)))
    ss.setdefault("st_i", 0)
    ss.setdefault("st_score", 0)
    if "st_cur" not in ss:
        ss.st_cur = new_item()
    st.subheader("🎯 Focus Challenge")
    st.caption("Pick the INK colour of the word, not what the word says.")

    if ss.st_i >= TOTAL:
        st.success(f"Round complete: {ss.st_score}/{TOTAL} correct 🎉")
        if st.button("Play again", type="primary"):
            ss.st_i, ss.st_score, ss.st_cur = 0, 0, new_item()
            st.rerun()
        return

    word, ink = ss.st_cur
    st.progress(ss.st_i / TOTAL, text=f"Question {ss.st_i + 1}/{TOTAL}")
    st.markdown(
        f'<div class="card" style="text-align:center;font-size:56px;font-weight:800;color:{STROOP_COLORS[ink]}">{word}</div>',
        unsafe_allow_html=True)
    cols = st.columns(len(STROOP_COLORS))
    for c, name in zip(cols, STROOP_COLORS):
        with c:
            if st.button(name, key=f"stb_{ss.st_i}_{name}", use_container_width=True):
                if name == ink:
                    ss.st_score += 1
                    add_points(5)
                ss.st_i += 1
                ss.st_cur = new_item()
                st.rerun()

def games_page():
    top_nav()
    st.title("🎮 Relax & Focus")
    st.caption("Short, non-clinical activities for pausing, resetting and refocusing.")
    st.metric("⭐ Points this session", st.session_state.get("points", 0))

    games = [
        ("reaction", "⚡", "Reaction Challenge", "Click the moment the box turns green."),
        ("memory", "🧠", "Memory Challenge", "Remember a growing letter sequence."),
        ("focus", "🎯", "Focus Challenge", "Pick the ink colour, ignore the word."),
        ("reset", "🌿", "Breathing Reset", "Guided 4-2-6 breathing pause."),
    ]
    cols = st.columns(4)
    for c, (gid, icon, title, desc) in zip(cols, games):
        with c:
            st.markdown(
                f'<div class="game-card"><div style="font-size:38px">{icon}</div><h4>{title}</h4><p class="muted">{desc}</p></div>',
                unsafe_allow_html=True)
            active = st.session_state.game == gid
            if st.button("Playing ▶" if active else "Play", key=f"g_{gid}",
                         use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.game = gid
                st.rerun()

    game = st.session_state.game
    if game:
        st.markdown("---")
        if game == "reaction":
            st.subheader("⚡ Reaction Challenge")
            st.caption("Real timing measured in your browser. Wait for green, then click fast.")
            components.html(REACTION_HTML, height=320)
        elif game == "memory":
            game_memory()
        elif game == "focus":
            game_stroop()
        elif game == "reset":
            st.subheader("🌿 One-Minute Reset")
            components.html(BREATH_HTML, height=340)
        if st.button("Close Activity"):
            st.session_state.game = None
            st.rerun()

# -------------------------
# WELFARE OFFICER
# -------------------------
def admin_dashboard():
    st.markdown("""
    <div class="hero">
        <h1>🛡️ Welfare Officer Portal</h1>
        <p>Authorized risk summaries • Explainable indicators • Human review</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout"):
        logout()

    # Build synthetic overview for demo + actual registered users
    personnel = list(USERS.keys())
    rows = []
    for u in personnel:
        h = get_history(u)
        if h:
            latest = h[-1]
            rows.append({
                "Personnel": u,
                "Risk": latest["risk"],
                "Trend": "Monitoring",
                "Last Assessment": latest["date"]
            })
        else:
            rows.append({
                "Personnel": u,
                "Risk": "LOW",
                "Trend": "No recent data",
                "Last Assessment": "—"
            })

    data = pd.DataFrame(rows)

    st.subheader("Organization Overview")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Personnel", len(data))
    with c2: st.metric("Low", int((data["Risk"]=="LOW").sum()))
    with c3: st.metric("Medium", int((data["Risk"]=="MEDIUM").sum()))
    with c4: st.metric("High", int((data["Risk"]=="HIGH").sum()))

    st.divider()
    st.subheader("Personnel Risk Overview")
    st.dataframe(data, use_container_width=True, hide_index=True)

    high = data[data["Risk"]=="HIGH"]
    if not high.empty:
        st.subheader("🚨 Priority Review")
        for _, row in high.iterrows():
            st.error(f'{row["Personnel"]} — HIGH — Multiple indicators require authorized review.')

    st.subheader("Personnel Summary")
    if len(data):
        selected = st.selectbox("Select personnel", data["Personnel"].tolist())
        row = data[data["Personnel"]==selected].iloc[0]
        st.write(f"### {selected}")
        a,b,c = st.columns(3)
        with a: st.metric("Risk", row["Risk"])
        with b: st.metric("Trend", row["Trend"])
        with c: st.metric("Last Assessment", row["Last Assessment"])

        h = get_history(selected)
        if h:
            df = pd.DataFrame(h)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["date"], y=df["score"], mode="lines+markers"))
            fig.update_layout(title="Risk Trend", template="plotly_white", height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.info("Officer view intentionally presents summarized welfare information rather than unrestricted raw personal data.")
        else:
            st.info("No completed assessment for this personnel account yet.")

# -------------------------
# ROUTING
# -------------------------
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.role == "personnel":
        if st.session_state.page == "dashboard":
            personnel_dashboard()
        elif st.session_state.page == "assessment":
            assessment_page()
        elif st.session_state.page == "result":
            result_page()
        elif st.session_state.page == "history":
            history_page()
        elif st.session_state.page == "games":
            games_page()
        elif st.session_state.page == "checkin":
            checkin_page()
        else:
            personnel_dashboard()
    elif st.session_state.role == "admin":
        admin_dashboard()
