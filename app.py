import streamlit as st
import uuid

import re


# ================= CONFIG =================
API_URL = "http://127.0.0.1:5000/emails"

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📩",
    layout="wide"
)

# ================= HEADER =================
st.markdown(
    "<h1 style='text-align:center;'>📩 AI-Powered Daily Email Summary</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:gray;'>Privacy-first assistant highlighting important emails, deadlines, and reminders</p>",
    unsafe_allow_html=True,
)

# ================= LOAD EMAILS =================
def load_emails():
    # Demo emails for Streamlit Cloud
    return [
        {
            "from": "college@university.edu",
            "subject": "Urgent: Assignment Deadline Tomorrow",
            "snippet": "Please submit your assignment before 11:59 PM tonight."
        },
        {
            "from": "internship@company.com",
            "subject": "Interview Schedule",
            "snippet": "Your interview is scheduled for next Monday at 10 AM."
        },
        {
            "from": "newsletter@shopping.com",
            "subject": "Big Sale This Weekend",
            "snippet": "Enjoy up to 70% off on selected items."
        }
    ]


# ================= REFRESH BUTTON =================
col_refresh_left, col_refresh_right = st.columns([8, 1])

with col_refresh_right:
    if st.button("🔄 Refresh"):
        st.session_state.emails = load_emails()

# First load
if "emails" not in st.session_state:
    st.session_state.emails = load_emails()

emails = st.session_state.emails

# ================= HELPERS =================
def is_important(email):
    words = ["urgent", "asap", "deadline", "important", "submit"]
    text = (email.get("subject", "") + email.get("snippet", "")).lower()
    return any(w in text for w in words)

def extract_deadline(email):
    match = re.search(r"\b(today|tomorrow|by\s[\w\s:]+)\b", email.get("snippet", ""), re.I)
    return match.group(0) if match else None

# ================= PROCESS EMAILS =================
for e in emails:
    e["id"] = e.get("id", str(uuid.uuid4()))
    e["important"] = is_important(e)
    e["deadline"] = extract_deadline(e)

# ================= SUMMARY CARDS =================
important = [e for e in emails if e["important"]]
deadlines = [e for e in emails if e["deadline"]]
total = len(emails)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div style="background:#ffdddd;padding:20px;border-radius:12px;text-align:center">
            <h3>🔥 Urgent Emails</h3>
            <h1>{len(important)}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div style="background:#ddeeff;padding:20px;border-radius:12px;text-align:center">
            <h3>⏰ Deadlines</h3>
            <h1>{len(deadlines)}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div style="background:#ddffdd;padding:20px;border-radius:12px;text-align:center">
            <h3>📨 Total Emails</h3>
            <h1>{total}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ================= DEADLINE SECTION =================
if deadlines:
    st.markdown("### 📝 Deadlines Detected")
    for d in deadlines:
        st.markdown(f"- **{d.get('subject','No Subject')}** → ⏰ {d['deadline']}")

st.divider()

# ================= EMAIL LIST =================
st.subheader("📬 Email Overview")

if not emails:
    st.info("No emails found. Click **Refresh** after starting Flask.")
else:
    for e in emails:
        card_color = "#fff6cc" if e["important"] else "#f5f5f5"

        with st.container():
            st.markdown(
                f"""
                <div style="
                    background:{card_color};
                    padding:18px;
                    border-radius:12px;
                    margin-bottom:10px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                ">
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 5])

            with col1:
                st.markdown(f"**From:** {e.get('sender','Unknown')}")
                st.markdown(f"**Subject:** {e.get('subject','No Subject')}")

            with col2:
                st.write(e.get("snippet", ""))

            st.markdown("</div>", unsafe_allow_html=True)
