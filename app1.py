
import streamlit as st
import requests

st.set_page_config(page_title="OWASP AI Assistant", layout="wide")
st.title("OWASP Top 10 Assistant")

# Sidebar model selector
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

# Input prompt
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
