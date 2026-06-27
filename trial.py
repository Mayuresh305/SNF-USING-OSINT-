import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import smtplib
import random
import time
from email.mime.text import MIMEText

st.set_page_config(page_title="Social Network Forensics", layout="wide")

# =========================
# EMAIL OTP CONFIG
# =========================
SENDER_EMAIL = "mayuresh.shinde3598@gmail.com"
SENDER_APP_PASSWORD = "jwkrfwfuoycrwnxa"

# =========================
# SESSION STATE
# =========================
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "verified" not in st.session_state:
    st.session_state.verified = False
if "sent_to" not in st.session_state:
    st.session_state.sent_to = ""
if "otp_time" not in st.session_state:
    st.session_state.otp_time = None

# =========================
# OTP FUNCTIONS
# =========================
def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(receiver_email: str, otp: str):
    subject = "Your Verification OTP"
    body = f"""
Hello,

Your OTP for Social Network Forensics verification is: {otp}

This OTP is valid for 5 minutes.

Regards,
Social Network Forensics System
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
    server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
    server.quit()

# =========================
# SOCIAL FORENSICS FUNCTIONS
# =========================
def get_profile(username):
    demo_profiles = {
        "real_user": {
            "username": "real_user",
            "followers": 850,
            "following": 180,
            "posts": 120,
            "default_pic": False,
            "account_age_days": 900
        },
        "fake_user": {
            "username": "fake_user",
            "followers": 12,
            "following": 1800,
            "posts": 2,
            "default_pic": True,
            "account_age_days": 8
        },
        "bot_account": {
            "username": "bot_account",
            "followers": 30,
            "following": 2200,
            "posts": 1,
            "default_pic": True,
            "account_age_days": 5
        }
    }

    if username in demo_profiles:
        return demo_profiles[username]

    base = sum(ord(c) for c in username)
    random.seed(base)

    return {
        "username": username,
        "followers": random.randint(20, 2000),
        "following": random.randint(100, 3000),
        "posts": random.randint(0, 100),
        "default_pic": random.choice([True, False]),
        "account_age_days": random.randint(5, 1500)
    }

def fake_score(profile):
    score = 0
    reasons = []

    if profile["followers"] < 50:
        score += 20
        reasons.append("Low followers")

    if profile["following"] > 1000:
        score += 20
        reasons.append("Very high following")

    if profile["posts"] < 5:
        score += 15
        reasons.append("Very low post count")

    if profile["default_pic"]:
        score += 25
        reasons.append("Default profile picture")

    if profile["account_age_days"] < 30:
        score += 20
        reasons.append("Newly created account")

    return min(score, 100), reasons

def create_graph(username):
    G = nx.Graph()
    G.add_node(username)

    if username == "real_user":
        linked_accounts = ["friend_1", "friend_2", "friend_3"]
    elif username == "fake_user":
        linked_accounts = ["bot_1", "bot_2", "spam_page", "suspicious_1"]
    elif username == "bot_account":
        linked_accounts = ["bot_7", "bot_9", "fake_user", "promo_linker"]
    else:
        linked_accounts = ["bot_1", "bot_2", "bot_3", "suspicious_1"]

    for acc in linked_accounts:
        G.add_node(acc)
        G.add_edge(username, acc)

    return G

# =========================
# UI
# =========================
st.title("Social Network Forensics Using OSINT")
st.subheader("Fake Profile Detection and Graph-Based Analysis")
st.write(
    )

# =========================
# EMAIL VERIFICATION SECTION
# =========================
st.header("Step 1: Real-Time Email Verification")
st.write("Verify your email first to access the analysis module.")

email = st.text_input("Enter your email address")

col1, col2 = st.columns(2)

with col1:
    if st.button("Send OTP"):
        if not email.strip():
            st.warning("Please enter an email address.")
        elif "@" not in email or "." not in email:
            st.warning("Please enter a valid email address.")
        elif SENDER_EMAIL == "yourgmail@gmail.com" or SENDER_APP_PASSWORD == "your16characterapppassword":
            st.error("Please update SENDER_EMAIL and SENDER_APP_PASSWORD in the code first.")
        else:
            otp = generate_otp()
            try:
                with st.spinner("Sending OTP to your email..."):
                    send_email_otp(email, otp)
                    time.sleep(1)

                st.session_state.generated_otp = otp
                st.session_state.otp_sent = True
                st.session_state.sent_to = email
                st.session_state.otp_time = time.time()
                st.session_state.verified = False

                st.success(f"OTP sent successfully to {email}")
            except Exception as e:
                st.error(f"Failed to send OTP: {e}")

with col2:
    if st.button("Reset Verification"):
        st.session_state.generated_otp = None
        st.session_state.otp_sent = False
        st.session_state.verified = False
        st.session_state.sent_to = ""
        st.session_state.otp_time = None
        st.rerun()

if st.session_state.otp_sent:
    st.info(f"OTP sent to: {st.session_state.sent_to}")
    entered_otp = st.text_input("Enter OTP", max_chars=6)

    if st.button("Verify OTP"):
        if not entered_otp.strip():
            st.warning("Please enter the OTP.")
        elif st.session_state.otp_time and (time.time() - st.session_state.otp_time > 300):
            st.error("OTP expired. Please request a new one.")
        elif entered_otp == st.session_state.generated_otp:
            st.session_state.verified = True
            st.success("Email verified successfully.")
        else:
            st.error("Invalid OTP.")

# =========================
# ANALYSIS SECTION
# =========================
if st.session_state.verified:
    st.header("Step 2: Social Profile Analysis")
    st.success("Access granted. You can now analyze profiles.")

    username = st.text_input("Enter Username (try: real_user, fake_user, bot_account)")

    if st.button("Analyze"):
        if username.strip() == "":
            st.warning("Please enter a username")
        else:
            with st.spinner("Collecting OSINT data from social media..."):
                time.sleep(2)

            st.success("Data successfully collected from OSINT sources")

            profile = get_profile(username)
            score, reasons = fake_score(profile)

            col3, col4 = st.columns(2)

            with col3:
                st.subheader("Profile Data")
                st.json(profile)

            with col4:
                st.subheader("Risk Score")
                st.metric("Fake Profile Score", f"{score}/100")

                if score >= 60:
                    st.error("High probability of fake account")
                elif score >= 40:
                    st.warning("Suspicious account")
                else:
                    st.success("Likely genuine account")

                st.write("### Reasons")
                for reason in reasons:
                    st.write(f"- {reason}")

            st.subheader("Graph-Based Analysis")
            st.write(
                "Each node represents an account, and edges represent suspicious or related connections."
            )

            G = create_graph(username)
            net = Network(height="500px", width="100%", notebook=False)
            net.from_nx(G)
            net.save_graph("graph.html")

            with open("graph.html", "r", encoding="utf-8") as f:
                graph_html = f.read()

            components.html(graph_html, height=550)
else:
    st.warning("Please complete email verification to unlock the analysis module.")