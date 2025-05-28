import streamlit as st
import requests
import urllib.parse
import jwt
from datetime import datetime
import time

# === Secure Configuration ===
st.set_page_config(
    page_title="OWASP AI Assistant",
    layout="wide",
    page_icon="🛡️"
)

# === Cognito Settings ===
COGNITO_DOMAIN = st.secrets["COGNITO_DOMAIN"]
CLIENT_ID = st.secrets["CLIENT_ID"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
COGNITO_LOGOUT_URL = (
    f"{COGNITO_DOMAIN}/logout?"
    f"client_id={CLIENT_ID}&"
    f"logout_uri={urllib.parse.quote(REDIRECT_URI)}"
)

# === Security Utilities ===
def generate_state_parameter():
    """Generate anti-CSRF state token"""
    return str(int(time.time()))

def get_secure_login_url():
    """Create login URL with state parameter"""
    state = generate_state_parameter()
    st.session_state.auth_state = state  # Store for validation later
    
    return (
        f"{COGNITO_DOMAIN}/oauth2/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope=openid+profile+email&"
        f"state={state}"
    )

def validate_state(state):
    """Verify state parameter matches original"""
    return state == st.session_state.get("auth_state")

def exchange_code_for_token(code):
    """Securely exchange auth code for tokens"""
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(
            token_url,
            data=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Authentication failed: {str(e)}")
        return None

def validate_jwt(token):
    """Validate JWT signature and claims"""
    try:
        # Get Cognito's public keys
        jwks_url = f"{COGNITO_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url, timeout=5).json()
        
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if not rsa_key:
            raise ValueError("No matching key found in JWKS")
        
        return jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=COGNITO_DOMAIN
        )
    except Exception as e:
        st.error(f"Token validation failed: {str(e)}")
        return None

# === Authentication Flow ===
def handle_auth_flow():
    query_params = st.query_params
    
    # Handle logout
    if "logout" in query_params:
        st.session_state.clear()
        st.rerun()
    
    # Handle OAuth callback
    if "code" in query_params and "state" in query_params:
        if not validate_state(query_params["state"][0]):
            st.error("Invalid state parameter - possible CSRF attack")
            return
        
        with st.spinner("Securely authenticating..."):
            token_data = exchange_code_for_token(query_params["code"][0])
            
            if token_data and "id_token" in token_data:
                # Validate token before storing
                claims = validate_jwt(token_data["id_token"])
                if claims:
                    st.session_state.auth = {
                        "tokens": token_data,
                        "claims": claims,
                        "expires_at": datetime.fromtimestamp(claims["exp"])
                    }
                    st.session_state.logged_in = True
                    st.query_params.clear()
                    st.rerun()

# === Secure UI Components ===
def show_login_buttons():
    """Render secure authentication options"""
    st.markdown("""
    <style>
        .auth-button {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: bold;
            width: 100%;
            text-align: center;
            margin: 0.5rem 0;
        }
        .auth-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    <div class="auth-container">
        <h2 style="text-align: center;">Secure Login</h2>
        <p style="text-align: center;">Please authenticate via AWS Cognito</p>
    """, unsafe_allow_html=True)

    login_url = get_secure_login_url()
    signup_url = f"{COGNITO_DOMAIN}/signup?client_id={CLIENT_ID}"
    
    # Using markdown with target="_blank" for security
    st.markdown(
        f"""
        <a href="{login_url}" target="_blank" class="auth-button" style="background-color: #4CAF50; color: white;">
            Login with Cognito
        </a>
        <a href="{signup_url}" target="_blank" class="auth-button" style="background-color: #2196F3; color: white;">
            Sign Up
        </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_user_profile():
    """Display authenticated user info"""
    if st.session_state.get("logged_in"):
        claims = st.session_state.auth["claims"]
        
        st.sidebar.markdown("### 🔐 Authenticated User")
        st.sidebar.write(f"**Email:** {claims.get('email')}")
        st.sidebar.write(f"**Expires:** {st.session_state.auth['expires_at'].strftime('%Y-%m-%d %H:%M')}")
        
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.markdown(
                f"<script>window.location.href='{COGNITO_LOGOUT_URL}';</script>",
                unsafe_allow_html=True
            )

# === Main App Execution ===
handle_auth_flow()

if not st.session_state.get("logged_in"):
    show_login_buttons()
    st.stop()  # Don't proceed unless authenticated

show_user_profile()

# Rest of your application code goes here...
# (Your existing page navigation and content)