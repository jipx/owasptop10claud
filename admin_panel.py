import streamlit as st

def admin_settings_panel(model_id_map):
    admin_token = st.text_input("Enter admin access code", type="password")
    if admin_token != st.secrets.get("ADMIN_TOKEN", "admin123"):
        st.warning("Access denied.")
        st.stop()

    st.markdown("### ⚙️ Administrator Control Panel")
    st.info("Configure global app settings or feature toggles below.")

    if "admin_settings" not in st.session_state:
        try:
            import json
            with open("admin_settings.json", "r") as f:
                st.session_state.admin_settings = json.load(f)
        except FileNotFoundError:
            st.session_state.admin_settings = {
                "enable_quiz": True,
                "default_model": "Claude 3.5 Sonnet"
            }

    settings = st.session_state.admin_settings

    enable_quiz = st.checkbox("Enable Adaptive Quiz", value=settings["enable_quiz"])
    default_model = st.selectbox("Default Model for All Pages", list(model_id_map.keys()), index=list(model_id_map.keys()).index(settings["default_model"]))

    if st.button("Save Settings"):
        settings["enable_quiz"] = enable_quiz
        settings["default_model"] = default_model
        with open("admin_settings.json", "w") as f:
            import json
            json.dump(settings, f)
        st.success("Settings updated and saved!")
