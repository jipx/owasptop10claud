import streamlit as st
import requests
import urllib.parse
import json
import jwt
from admin_panel import admin_settings_panel

# === App Layout ===
st.set_page_config(page_title="OWASP AI Assistant", layout="wide")

# === Cognito Config ===
COGNITO_DOMAIN = st.secrets["COGNITO_DOMAIN"]
CLIENT_ID = st.secrets["CLIENT_ID"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
LOGOUT_URL = (
    f"{COGNITO_DOMAIN}/logout"
    f"?client_id={CLIENT_ID}&logout_uri={urllib.parse.quote(REDIRECT_URI)}"
)

# === Auth Utilities ===
def get_login_url():
    return (
        f"{COGNITO_DOMAIN}/oauth2/authorize?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=openid+profile+email"
    )

def exchange_code_for_token(code):
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)
    return response.json()

# === Handle Logout via Query Params ===
query_params = st.query_params
if "logout" in query_params:
    st.session_state.clear()
    st.markdown(f"<meta http-equiv='refresh' content='0; URL={LOGOUT_URL}' />", unsafe_allow_html=True)
    st.stop()

# === Handle Login Callback ===
if "code" in query_params:
    token_info = exchange_code_for_token(query_params["code"][0])
    if "id_token" in token_info:
        st.session_state["id_token"] = token_info["id_token"]
        st.session_state["access_token"] = token_info.get("access_token")
        st.session_state["logged_in"] = True
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Login failed. Please try again.")

# === UI: Login / Logout ===
if st.session_state.get("logged_in"):
    st.success("✅ Logged in with Cognito")
    try:
        decoded_token = jwt.decode(
            st.session_state["id_token"],
            options={"verify_signature": False}
        )
        email = decoded_token.get("email", "N/A")
        sub = decoded_token.get("sub", "N/A")
        st.sidebar.markdown("### 👤 Profile Info")
        st.sidebar.write(f"**Email:** {email}")
        st.sidebar.write(f"**User ID:** {sub}")
    except Exception as e:
        st.sidebar.error("Failed to decode ID token.")
        st.sidebar.write(str(e))

    # Button-triggered logout
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.markdown(f"<meta http-equiv='refresh' content='0; URL={LOGOUT_URL}' />", unsafe_allow_html=True)
        st.stop()

else:
    login_url = get_login_url()
    signup_url = (
        f"{COGNITO_DOMAIN}/signup?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=openid+profile+email"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login with Cognito"):
            st.markdown(f"<meta http-equiv='refresh' content='0; URL={login_url}' />", unsafe_allow_html=True)
    with col2:
        if st.button("Sign Up"):
            st.markdown(f"<meta http-equiv='refresh' content='0; URL={signup_url}' />", unsafe_allow_html=True)

# === UI Utilities ===
def banner(title: str, color: str = "#1f77b4"):
    st.markdown(f"""
    <div style='padding: 0.75em; margin: 1em 0; background-color: {color}; color: white;
                border-radius: 0.5em; font-weight: bold; font-size: 1.2em;'>
        {title}
    </div>
    """, unsafe_allow_html=True)

# === Navigation Sidebar ===
page = st.sidebar.radio(
    "Navigation",
    [
        "🔐 OWASP Top 10",
        "🛠️ WebGoat",
        "🎓 Mimosa (for tutor only)",
        "☁️ Cloud Security",
        "🤖 LLM Application Security",
        "🧠 Adaptive Quiz",
        "⚙️ Administrator Settings"
    ]
)

model_choice = st.sidebar.selectbox(
    "Choose a model",
    ["Claude 3.5 Sonnet", "Claude v2", "DeepSeek-V2 Chat"]
)

model_id_map = {
    "Claude 3.5 Sonnet": "anthropic.claude-3-sonnet-20240620-v1:0",
    "Claude v2": "anthropic.claude-v2",
    "DeepSeek-V2 Chat": "deepseek.chat"
}

selected_model_id = model_id_map[model_choice]

# === Page Logic ===
if page == "🧠 Adaptive Quiz":
    banner("🧠 Adaptive Quiz Generator", "#444444")
    difficulty = st.selectbox("Choose difficulty", ["Beginner", "Intermediate", "Advanced"])
    topic = st.text_input("Quiz Topic (e.g., XSS, IAM, Prompt Injection)")
    if st.button("Generate Quiz Question"):
        quiz_prompt = f"Generate a {difficulty.lower()} level multiple choice question on {topic}. Include 4 options and indicate the correct answer."
        with st.spinner("Generating quiz..."):
            try:
                response = requests.post(
                    "https://5olh8uhg6b.execute-api.ap-northeast-1.amazonaws.com/prod/ask",
                    json={"prompt": quiz_prompt, "modelId": selected_model_id},
                    headers={"Content-Type": "application/json"}
                )
                result = response.json()
                output = result.get("response") or result.get("error") or result or "[No output returned]"
                if response.status_code == 200:
                    st.markdown(output, unsafe_allow_html=True)
                else:
                    st.error(f"API Error {response.status_code}")
                    st.code(output)
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "⚙️ Administrator Settings":
    banner("⚙️ Administrator Control Panel", "#333333")
    admin_settings_panel(model_id_map)

else:
    section_colors = {
        "🔐 OWASP Top 10": "#d7263d",
        "🛠️ WebGoat": "#ff6f00",
        "🎓 Mimosa (for tutor only)": "#5d2e8c",
        "☁️ Cloud Security": "#208b3a",
        "🤖 LLM Application Security": "#3e4e88"
    }
    banner(page, section_colors.get(page, "#1f77b4"))
    prompt = st.text_area("Ask a question about OWASP vulnerabilities")
    if st.button("Submit"):
        if not prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Contacting model..."):
                try:
                    response = requests.post(
                        "https://5olh8uhg6b.execute-api.ap-northeast-1.amazonaws.com/prod/ask",
                        json={"prompt": prompt, "modelId": selected_model_id},
                        headers={"Content-Type": "application/json"}
                    )
                    try:
                        result = response.json()
                        output = result.get("response") or result.get("error") or result or "[No output returned]"
                        if response.status_code == 200:
                            st.success("Model Response:")
                            st.markdown(output, unsafe_allow_html=True)
                        else:
                            st.error(f"API Error {response.status_code}")
                            st.code(output)
                    except Exception as parse_error:
                        st.error("⚠️ Failed to parse response from API.")
                        st.code(response.text)
                except Exception as e:
                    st.error(f"Error contacting API: {e}")

st.markdown("---")
st.markdown("Built with Amazon Bedrock, Streamlit, and OWASP guidance.")
