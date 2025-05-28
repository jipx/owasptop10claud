import streamlit as st
import requests
import urllib.parse
import json
import jwt
from admin_panel import admin_settings_panel
import time

# === App Layout ===
st.set_page_config(
    page_title="OWASP AI Assistant",
    layout="wide",
    page_icon="🛡️"
)

# === Cognito Config ===
COGNITO_DOMAIN = st.secrets["COGNITO_DOMAIN"]
CLIENT_ID = st.secrets["CLIENT_ID"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
LOGOUT_URL = (
    f"{COGNITO_DOMAIN}/logout?"
    f"client_id={CLIENT_ID}&"
    f"logout_uri={urllib.parse.quote(REDIRECT_URI)}"
)

# === Auth Utilities ===
def get_login_url():
    return (
        f"{COGNITO_DOMAIN}/oauth2/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope=openid+profile+email&"
        f"state={urllib.parse.quote(REDIRECT_URI)}"
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
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Token exchange failed: {str(e)}")
        return None

def validate_token(token):
    try:
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        # Check if token is expired
        if decoded.get("exp", 0) < time.time():
            return None
        return decoded
    except jwt.PyJWTError as e:
        st.error(f"Token validation error: {str(e)}")
        return None

# === Session State Management ===
def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}

# === Handle Authentication Flow ===
def handle_auth_flow():
    query_params = st.query_params
    
    # Handle logout
    if "logout" in query_params:
        st.session_state.clear()
        st.markdown(
            f"<meta http-equiv='refresh' content='0; URL={LOGOUT_URL}' />", 
            unsafe_allow_html=True
        )
        st.stop()
    
    # Handle login callback
    if "code" in query_params:
        with st.spinner("Authenticating..."):
            token_info = exchange_code_for_token(query_params["code"][0])
            if token_info and "id_token" in token_info:
                st.session_state["tokens"] = token_info
                st.session_state["logged_in"] = True
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Login failed. Please try again.")
                time.sleep(2)
                st.rerun()

# === UI Components ===
def show_auth_buttons():
    login_url = get_login_url()
    signup_url = (
        f"{COGNITO_DOMAIN}/signup?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope=openid+profile+email"
    )

    st.markdown("""
    <div style='text-align: center; margin: 2rem 0;'>
        <h2>OWASP AI Assistant</h2>
        <p>Please authenticate to access security resources</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Login with Cognito", login_url)
    with col2:
        st.link_button("Sign Up", signup_url)

def show_user_profile():
    if "tokens" in st.session_state:
        user_info = validate_token(st.session_state["tokens"]["id_token"])
        if user_info:
            st.session_state.user_info = {
                "email": user_info.get("email", "N/A"),
                "user_id": user_info.get("sub", "N/A"),
                "name": user_info.get("name", "N/A")
            }
    
    st.sidebar.success("✅ Authenticated")
    st.sidebar.markdown("### 👤 User Profile")
    st.sidebar.write(f"**Name:** {st.session_state.user_info.get('name')}")
    st.sidebar.write(f"**Email:** {st.session_state.user_info.get('email')}")
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.markdown(
            f"<meta http-equiv='refresh' content='0; URL={LOGOUT_URL}' />", 
            unsafe_allow_html=True
        )
        st.stop()

def banner(title: str, color: str = "#1f77b4"):
    st.markdown(f"""
    <div style='padding: 0.75em; margin: 1em 0; background-color: {color}; color: white;
                border-radius: 0.5em; font-weight: bold; font-size: 1.2em;'>
        {title}
    </div>
    """, unsafe_allow_html=True)

# === Main App Logic ===
initialize_session()
handle_auth_flow()

if not st.session_state.get("logged_in"):
    show_auth_buttons()
    st.stop()

show_user_profile()

# === Navigation Sidebar ===
PAGE_OPTIONS = [
    "🔐 OWASP Top 10",
    "🛠️ WebGoat",
    "🎓 Mimosa (for tutor only)",
    "☁️ Cloud Security",
    "🤖 LLM Application Security",
    "🧠 Adaptive Quiz",
    "⚙️ Administrator Settings"
]

page = st.sidebar.radio("Navigation", PAGE_OPTIONS)

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

# === Page Handlers ===
def call_bedrock_api(prompt, model_id):
    try:
        response = requests.post(
            "https://5olh8uhg6b.execute-api.ap-northeast-1.amazonaws.com/prod/ask",
            json={"prompt": prompt, "modelId": model_id},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def handle_quiz_page():
    banner("🧠 Adaptive Quiz Generator", "#444444")
    difficulty = st.selectbox("Choose difficulty", ["Beginner", "Intermediate", "Advanced"])
    topic = st.text_input("Quiz Topic (e.g., XSS, IAM, Prompt Injection)")
    
    if st.button("Generate Quiz Question"):
        quiz_prompt = (
            f"Generate a {difficulty.lower()} level multiple choice question on {topic}. "
            f"Include 4 options and indicate the correct answer."
        )
        with st.spinner("Generating quiz..."):
            result = call_bedrock_api(quiz_prompt, selected_model_id)
            if result:
                output = result.get("response") or "[No output returned]"
                st.markdown(output, unsafe_allow_html=True)

def handle_admin_page():
    banner("⚙️ Administrator Control Panel", "#333333")
    if st.session_state.user_info.get("email") in st.secrets.get("ADMIN_EMAILS", []):
        admin_settings_panel(model_id_map)
    else:
        st.warning("⚠️ You don't have administrator privileges.")

def handle_default_page(page_name):
    section_colors = {
        "🔐 OWASP Top 10": "#d7263d",
        "🛠️ WebGoat": "#ff6f00",
        "🎓 Mimosa (for tutor only)": "#5d2e8c",
        "☁️ Cloud Security": "#208b3a",
        "🤖 LLM Application Security": "#3e4e88"
    }
    banner(page_name, section_colors.get(page_name, "#1f77b4"))
    
    prompt = st.text_area("Ask a question about OWASP vulnerabilities")
    if st.button("Submit"):
        if not prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating response..."):
                result = call_bedrock_api(prompt, selected_model_id)
                if result:
                    output = result.get("response") or "[No output returned]"
                    st.success("Model Response:")
                    st.markdown(output, unsafe_allow_html=True)

# === Page Routing ===
if page == "🧠 Adaptive Quiz":
    handle_quiz_page()
elif page == "⚙️ Administrator Settings":
    handle_admin_page()
else:
    handle_default_page(page)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "Built with Amazon Bedrock, Streamlit, and OWASP guidance."
    "</div>",
    unsafe_allow_html=True
)