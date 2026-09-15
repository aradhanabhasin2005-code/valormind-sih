
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# ============================================================
# VALORMIND - SIH PROTOTYPE
# ============================================================

st.set_page_config(
    page_title="VALORMIND",
    page_icon="🛡️",
    layout="wide"
)

# -------------------------
# CUSTOM CSS
# -------------------------

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(135deg,#0f172a,#1e3a5f);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.risk-low {
    background: #dcfce7;
    color: #166534;
    padding: 15px;
    border-radius: 12px;
    font-weight: bold;
}

.risk-medium {
    background: #fef3c7;
    color: #92400e;
    padding: 15px;
    border-radius: 12px;
    font-weight: bold;
}

.risk-high {
    background: #fee2e2;
    color: #991b1b;
    padding: 15px;
    border-radius: 12px;
    font-weight: bold;
}

.small {
    color: #64748b;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DEMO DATA
# ============================================================

USERS = {
    "person001": {
        "pin": "1234",
        "name": "Personnel 001",
        "role": "personnel"
    },
    "person002": {
        "pin": "2345",
        "name": "Personnel 002",
        "role": "personnel"
    },
    "person003": {
        "pin": "3456",
        "name": "Personnel 003",
        "role": "personnel"
    },
    "person004": {
        "pin": "4567",
        "name": "Personnel 004",
        "role": "personnel"
    },
    "person005": {
        "pin": "5678",
        "name": "Personnel 005",
        "role": "personnel"
    },
    "person006": {
        "pin": "6789",
        "name": "Personnel 006",
        "role": "personnel"
    }
}

ADMIN = {
    "admin": {
        "pin": "9999",
        "name": "Welfare Officer"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None


# ============================================================
# RISK ENGINE
# ============================================================

def calculate_risk(reaction_time, go_errors, memory_accuracy,
                   stroop_accuracy, attention_accuracy,
                   stress, fatigue, sleep):

    score = 0

    # Cognitive indicators
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

    # Self reported
    if stress >= 8:
        score += 10
    elif stress >= 6:
        score += 5

    if fatigue >= 8:
        score += 10
    elif fatigue >= 6:
        score += 5

    # Sleep
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

    return risk, score


# ============================================================
# LOGIN
# ============================================================

def login_page():

    st.markdown("""
    <div class="hero">
        <h1>🛡️ VALORMIND</h1>
        <p>Personalized Personnel Welfare & Cognitive Risk Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Privacy-first prototype: demo data only. "
        "No classified or operational information is required."
    )

    portal = st.radio(
        "Select Portal",
        ["Personnel Portal", "Welfare Officer Portal"],
        horizontal=True
    )

    username = st.text_input("Username")
    pin = st.text_input("PIN", type="password")

    if st.button("Secure Login", type="primary"):

        if portal == "Personnel Portal":

            if username in USERS and USERS[username]["pin"] == pin:

                st.session_state.logged_in = True
                st.session_state.role = "personnel"
                st.session_state.user = username

                st.rerun()

            else:
                st.error("Invalid username or PIN.")

        else:

            if username in ADMIN and ADMIN[username]["pin"] == pin:

                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.user = username

                st.rerun()

            else:
                st.error("Invalid Welfare Officer credentials.")


# ============================================================
# PERSONNEL DASHBOARD
# ============================================================

def personnel_dashboard():

    user = USERS[st.session_state.user]

    st.markdown("""
    <div class="hero">
        <h1>Personnel Dashboard</h1>
        <p>Private • Personalized • Continuous Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Risk", "MEDIUM", "↓ Improving")

    with col2:
        st.metric("Baseline Stability", "82%", "+4%")

    with col3:
        st.metric("Last Assessment", "Today")

    with col4:
        st.metric("Monitoring Days", "14")

    st.divider()

    st.subheader("🧠 Cognitive Performance")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Reaction Time", "328 ms", "+8 ms")

    with c2:
        st.metric("Attention", "86%", "+3%")

    with c3:
        st.metric("Working Memory", "84%", "-2%")

    st.subheader("📈 Personal Trend")

    dates = pd.date_range(end=datetime.now(), periods=14)

    baseline = np.array(
        [82,84,83,85,86,84,87,86,85,83,81,79,80,82]
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=baseline,
        mode="lines+markers",
        name="Performance Index",
        line=dict(color="#2563eb", width=3)
    ))

    fig.add_hline(
        y=75,
        line_dash="dash",
        line_color="orange",
        annotation_text="Monitoring Threshold"
    )

    fig.update_layout(
        height=350,
        template="plotly_white",
        yaxis_title="Performance Index",
        xaxis_title="Date"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💡 Personalized Recommendation")

    st.success(
        "Your current indicators show a mild deviation from your personal baseline. "
        "Consider adequate recovery and complete a follow-up assessment."
    )

    st.caption(
        "This prototype provides risk indicators and does not diagnose medical or psychological conditions."
    )

    if st.button("Start Quick Assessment", type="primary"):
        st.session_state.page = "assessment"
        st.rerun()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


# ============================================================
# COGNITIVE ASSESSMENT
# ============================================================

def assessment_page():

    st.title("🧠 Quick Cognitive & Wellness Assessment")

    st.info(
        "This demonstration uses short cognitive tasks and voluntary wellness inputs. "
        "Results are compared with the individual's baseline."
    )

    st.subheader("1. Reaction Time")

    st.write(
        "For the prototype, enter the measured average reaction time "
        "from the reaction-time task."
    )

    reaction_time = st.number_input(
        "Average Reaction Time (ms)",
        min_value=150,
        max_value=1000,
        value=320
    )

    st.subheader("2. Go / No-Go")

    go_errors = st.slider(
        "Incorrect responses",
        0, 15, 2
    )

    st.subheader("3. Working Memory — 2-Back")

    memory_accuracy = st.slider(
        "Accuracy (%)",
        0, 100, 85
    )

    st.subheader("4. Stroop Test")

    stroop_accuracy = st.slider(
        "Accuracy (%)",
        0, 100, 88
    )

    st.subheader("5. Sustained Attention")

    attention_accuracy = st.slider(
        "Accuracy (%)",
        0, 100, 90
    )

    st.subheader("6. Wellness Check-In")

    stress = st.slider(
        "Current perceived stress",
        0, 10, 4
    )

    fatigue = st.slider(
        "Current fatigue",
        0, 10, 4
    )

    sleep = st.slider(
        "Sleep duration last night (hours)",
        0.0, 12.0, 7.0, 0.5
    )

    if st.button("Analyze My Results", type="primary"):

        risk, score = calculate_risk(
            reaction_time,
            go_errors,
            memory_accuracy,
            stroop_accuracy,
            attention_accuracy,
            stress,
            fatigue,
            sleep
        )

        st.session_state.assessment_result = {
            "risk": risk,
            "score": score
        }

        st.session_state.page = "result"

        st.rerun()

    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


# ============================================================
# RESULT PAGE
# ============================================================

def result_page():

    result = st.session_state.get("assessment_result")

    st.title("VALORMIND Assessment Result")

    if not result:
        st.warning("No assessment available.")
        return

    risk = result["risk"]
    score = result["score"]

    if risk == "LOW":

        st.markdown(
            '<div class="risk-low">🟢 LOW RISK</div>',
            unsafe_allow_html=True
        )

        st.success(
            "No significant concerning deviation detected in this assessment."
        )

    elif risk == "MEDIUM":

        st.markdown(
            '<div class="risk-medium">🟡 MEDIUM RISK</div>',
            unsafe_allow_html=True
        )

        st.warning(
            "Some indicators show a meaningful deviation. "
            "Continued monitoring and appropriate recovery/support are recommended."
        )

    else:

        st.markdown(
            '<div class="risk-high">🔴 HIGH RISK</div>',
            unsafe_allow_html=True
        )

        st.error(
            "Multiple indicators require attention. "
            "Human review by an authorized Welfare Officer is recommended."
        )

    st.metric("Risk Index", f"{score}/100")

    st.subheader("🔎 Contributing Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("🧠 Cognitive Performance")
        st.write("Reaction time, attention and memory")

    with col2:
        st.write("😴 Recovery")
        st.write("Sleep and fatigue indicators")

    with col3:
        st.write("📝 Wellness")
        st.write("Self-reported stress indicators")

    st.info(
        "Risk indication is a decision-support output, not a medical diagnosis."
    )

    if risk == "HIGH":
        st.warning(
            "An authorized Welfare Officer should review the case before any intervention."
        )

    if st.button("Return to Dashboard", type="primary"):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard():

    st.markdown("""
    <div class="hero">
        <h1>Welfare Officer Portal</h1>
        <p>Authorized Risk Monitoring & Human Intervention</p>
    </div>
    """, unsafe_allow_html=True)

    data = pd.DataFrame({
        "Personnel": [
            "P-001", "P-002", "P-003",
            "P-004", "P-005", "P-006"
        ],
        "Risk": [
            "LOW", "MEDIUM", "LOW",
            "HIGH", "MEDIUM", "LOW"
        ],
        "Trend": [
            "Stable", "Increasing", "Stable",
            "Increasing", "Stable", "Improving"
        ],
        "Last Assessment": [
            "Today", "Today", "Yesterday",
            "Today", "Today", "Yesterday"
        ]
    })

    st.subheader("Organization Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Personnel", "6")

    with c2:
        st.metric("Low Risk", "3")

    with c3:
        st.metric("Medium Risk", "2")

    with c4:
        st.metric("High Risk", "1")

    st.divider()

    st.subheader("Personnel Risk Overview")

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🚨 Priority Review")

    st.error(
        "P-004 — HIGH RISK — Multiple indicators show deterioration from personal baseline."
    )

    st.write(
        "The officer dashboard intentionally shows summarized risk information "
        "rather than unrestricted raw personal data."
    )

    selected = st.selectbox(
        "View Personnel Summary",
        data["Personnel"]
    )

    row = data[data["Personnel"] == selected].iloc[0]

    st.subheader(f"Personnel Profile — {selected}")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Risk Level", row["Risk"])

    with c2:
        st.metric("Trend", row["Trend"])

    with c3:
        st.metric("Last Assessment", row["Last Assessment"])

    dates = pd.date_range(end=datetime.now(), periods=10)

    if selected == "P-004":
        values = [91,89,88,86,84,81,77,73,69,65]
    elif selected == "P-002":
        values = [75,77,76,74,73,72,70,68,66,64]
    else:
        values = [75,77,78,79,80,81,82,83,84,85]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode="lines+markers",
        line=dict(color="#dc2626" if row["Risk"]=="HIGH" else "#2563eb")
    ))

    fig.update_layout(
        title="Performance Trend vs Personal Baseline",
        template="plotly_white",
        height=320
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recommended Action")

    if row["Risk"] == "HIGH":

        st.error(
            "Human review recommended. Consider welfare follow-up according to organizational policy."
        )

        if st.button("Mark Review as Initiated"):
            st.success("Review status updated.")

    elif row["Risk"] == "MEDIUM":

        st.warning(
            "Continue monitoring and consider appropriate support."
        )

    else:

        st.success(
            "No immediate intervention indicated."
        )

    st.caption(
        "Access is restricted to authorized welfare information. "
        "This is a demonstration using synthetic data."
    )

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


# ============================================================
# ROUTING
# ============================================================

if not st.session_state.logged_in:

    login_page()

else:

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    if st.session_state.role == "personnel":

        if st.session_state.page == "dashboard":
            personnel_dashboard()

        elif st.session_state.page == "assessment":
            assessment_page()

        elif st.session_state.page == "result":
            result_page()

    elif st.session_state.role == "admin":

        admin_dashboard()
