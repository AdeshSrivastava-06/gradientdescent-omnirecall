import streamlit as st
from search import answer_question, generate_daily_summary
from db import get_all_app_settings, set_app_blocked, add_custom_app, get_captures_in_range
from datetime import datetime, timedelta

st.set_page_config(page_title="OmniRecall", layout="wide")

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .main .block-container {
        max-width: 1100px;
        margin: 0 auto;
        padding-top: 3rem;
    }
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 3rem;
        letter-spacing: -0.5px;
        color: #F5F5F5 !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        text-align: center;
        font-size: 1.1rem;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        border: 1px solid #2A2E37;
        background-color: #161A23;
        padding: 0.9rem;
        font-size: 1.05rem;
    }
    .stButton button {
        border-radius: 8px;
        border: none;
        background-color: #6C5CE7;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        font-size: 1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #5B4CDB;
        color: white;
    }
    [data-testid="stMetric"] {
        background-color: #161A23;
        border-radius: 10px;
        padding: 0.8rem;
        border: 1px solid #2A2E37;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-size: 1.05rem;
    }
    hr {
        border-color: #2A2E37 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("OmniRecall")
st.caption("Your local screen memory — fully offline, entirely private.")
st.markdown("<br>", unsafe_allow_html=True)

tab_search, tab_timetravel, tab_summary, tab_privacy = st.tabs(
    ["Search", "Time Travel", "Daily Summary", "Privacy Settings"]
)

# ---------------- SEARCH TAB ----------------
with tab_search:
    query = st.text_input("What are you trying to remember?", placeholder="e.g. what was that recipe I saw earlier")

    if st.button("Search") and query.strip():
        with st.spinner("Searching your screen memory..."):
            answer, matches = answer_question(query)

        st.subheader("Answer")
        st.markdown(answer)

        if matches:
            best_score, best_cap = matches[0]
            if best_score < 0.4:
                st.warning("Low confidence match — this might not be exactly what you're looking for.")

            st.subheader("Best Match")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Confidence", f"{int(best_score * 100)}%")
            with col2:
                st.markdown(f"**Captured:** {best_cap['timestamp']}  \n*{best_cap.get('app_name', '')}*")
            if best_cap.get("screenshot_path"):
                st.image(best_cap["screenshot_path"], use_container_width=True)
            else:
                st.caption("Screenshot was archived — text-only record retained.")

            if len(matches) > 1:
                with st.expander("Not what you were looking for? Show more matches"):
                    for score, cap in matches[1:]:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.metric("Confidence", f"{int(score * 100)}%")
                        with col2:
                            st.markdown(f"**Captured:** {cap['timestamp']}  \n*{cap.get('app_name', '')}*")
                        if cap.get("screenshot_path"):
                            st.image(cap["screenshot_path"], use_container_width=True)
                        else:
                            st.caption("Screenshot was archived — text-only record retained.")
                        st.divider()

# ---------------- TIME TRAVEL TAB ----------------
with tab_timetravel:
    st.subheader("Browse your last 3 hours")
    st.caption("Scroll through everything captured recently, in order.")

    now = datetime.now()
    start = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    end = now.strftime("%Y-%m-%d %H:%M:%S")
    recent_captures = get_captures_in_range(start, end)

    if not recent_captures:
        st.info("No captures in the last 3 hours yet.")
    elif len(recent_captures) == 1:
        cap = recent_captures[0]
        st.markdown(f"**{cap['timestamp']}** — *{cap.get('app_name', 'Unknown')}*")
        if cap.get("screenshot_path"):
            st.image(cap["screenshot_path"], use_container_width=True)
        else:
            st.caption("Screenshot archived — showing text only.")
        with st.expander("Extracted text"):
            st.text(cap["text"])
    else:
        index = st.slider("Timeline", 0, len(recent_captures) - 1, len(recent_captures) - 1)
        cap = recent_captures[index]

        st.markdown(f"**{cap['timestamp']}** — *{cap.get('app_name', 'Unknown')}*")
        if cap.get("screenshot_path"):
            st.image(cap["screenshot_path"], use_container_width=True)
        else:
            st.caption("Screenshot archived — showing text only.")
        with st.expander("Extracted text"):
            st.text(cap["text"])

# ---------------- DAILY SUMMARY TAB ----------------
with tab_summary:
    st.subheader("What did I do today?")
    if st.button("Generate Summary"):
        with st.spinner("Summarizing today's activity..."):
            summary = generate_daily_summary()
        st.markdown(summary)

# ---------------- PRIVACY / BLOCKED APPS TAB ----------------
with tab_privacy:
    st.subheader("Blocked Applications")
    st.caption("Apps in this list are never captured or indexed, even if visible on screen.")

    settings = get_all_app_settings()

    if settings:
        for entry in settings:
            app_name = entry["app_name"]
            currently_blocked = entry["blocked"]
            new_value = st.checkbox(app_name, value=currently_blocked, key=f"block_{app_name}")
            if new_value != currently_blocked:
                set_app_blocked(app_name, new_value)
                st.rerun()
    else:
        st.info("No app settings found yet.")

    st.divider()
    st.subheader("Add a custom app to block")
    with st.form("add_app_form", clear_on_submit=True):
        new_app_name = st.text_input("Window title or app name (partial match, case-insensitive)")
        submitted = st.form_submit_button("Add & Block")
        if submitted and new_app_name.strip():
            add_custom_app(new_app_name.strip(), blocked=True)
            st.success(f"'{new_app_name.strip()}' added and blocked.")
            st.rerun()
