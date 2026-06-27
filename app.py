import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="OSINT Instagram Forensics", layout="wide")

st.title("Social Network Forensics Using OSINT")
st.subheader("Fake Profile Detection & Graph-Based Analysis")

# 🔹 INPUT
username = st.text_input("Enter Instagram Username")


# 🔹 CONTROLLED PROFILE GENERATION (REALISTIC PATTERNS)
def generate_profile(username):
    profile_type = random.choice(["fake", "real", "suspicious"])

    if profile_type == "fake":
        return {
            "username": username,
            "followers": random.randint(0, 50),
            "following": random.randint(800, 2000),
            "posts": random.randint(0, 5),
            "account_age_days": random.randint(1, 30),
            "bio": random.choice(["Follow me", "DM for promo", "Crypto 🚀"]),
            "profile_pic": False,
        }

    elif profile_type == "suspicious":
        return {
            "username": username,
            "followers": random.randint(20, 200),
            "following": random.randint(300, 1200),
            "posts": random.randint(2, 15),
            "account_age_days": random.randint(20, 100),
            "bio": random.choice(["Official", "", "Check my page"]),
            "profile_pic": random.choice([True, False]),
        }

    else:  # real
        return {
            "username": username,
            "followers": random.randint(200, 2000),
            "following": random.randint(100, 800),
            "posts": random.randint(20, 200),
            "account_age_days": random.randint(200, 2000),
            "bio": "Personal account",
            "profile_pic": True,
        }


# 🔹 IMPROVED FAKE SCORE (WEIGHTED LOGIC)
def fake_score(profile):
    score = 0
    reasons = []

    followers = profile["followers"]
    following = profile["following"]
    posts = profile["posts"]
    age = profile["account_age_days"]
    bio = profile["bio"].lower()
    pic = profile["profile_pic"]

    # 1. Followers
    if followers < 50:
        score += 20
        reasons.append("Very low followers")

    # 2. Following
    if following > 1000:
        score += 20
        reasons.append("Excessive following")

    # 3. Posts
    if posts < 5:
        score += 15
        reasons.append("Low content activity")

    # 4. Account Age
    if age < 30:
        score += 20
        reasons.append("New account")

    # 5. Profile Picture
    if not pic:
        score += 10
        reasons.append("No profile picture")

    # 6. Bio analysis
    suspicious_words = ["follow", "dm", "promo", "crypto"]
    if any(word in bio for word in suspicious_words):
        score += 10
        reasons.append("Suspicious bio keywords")

    # 7. Ratio analysis
    if followers > 0:
        ratio = following / followers
        if ratio > 10:
            score += 15
            reasons.append("Abnormal follower-following ratio")

    return min(score, 100), reasons


# 🔹 GRAPH ANALYSIS
def create_graph(username, profile):
    G = nx.Graph()
    G.add_node(username)

    # suspicious cluster
    if profile["followers"] < 50:
        bots = [f"bot_{i}" for i in range(1, 5)]
        for b in bots:
            G.add_node(b)
            G.add_edge(username, b)

    # hashtag cluster
    tags = ["#followback", "#crypto", "#promo"]
    for tag in tags:
        G.add_node(tag)
        G.add_edge(username, tag)

    return G


# 🔹 GRAPH RENDER
def render_graph(G):
    net = Network(height="500px", width="100%")
    net.from_nx(G)
    net.save_graph("graph.html")

    with open("graph.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=550)


# 🚀 MAIN
if st.button("Analyze Profile"):

    if username.strip() == "":
        st.warning("Enter username")

    else:
        profile = generate_profile(username)
        score, reasons = fake_score(profile)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Profile Data")
            st.json(profile)

        with col2:
            st.subheader("Fake Profile Score")
            st.metric("Score", f"{score}/100")

            if score >= 70:
                st.error("Highly Fake Account 🚨")
            elif score >= 40:
                st.warning("Suspicious Account ⚠️")
            else:
                st.success("Likely Genuine ✅")

            st.write("### Detection Reasons")
            for r in reasons:
                st.write(f"- {r}")

        st.subheader("Graph-Based Analysis")
        G = create_graph(username, profile)
        render_graph(G)