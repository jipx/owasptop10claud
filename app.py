
import streamlit as st
import requests

st.set_page_config(page_title="OWASP Assistant", layout="centered")
st.title("OWASP Top 10 Assistant (Claude via API Gateway)")

st.markdown("Ask a security-related question powered by Amazon Bedrock's Claude model.")

api_url = st.text_input("API Gateway Endpoint URL", "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/ask")

prompt = st.text_area("Enter your question:", "How do I prevent SQL Injection in Python?")

if st.button("Ask Claude"):
    if not api_url.startswith("https://"):
        st.error("Please enter a valid API Gateway URL.")
    else:
        with st.spinner("Waiting for Claude..."):
            try:
                response = requests.post(api_url, json={"prompt": prompt})
                data = response.json()
                st.success("Claude says:")
                st.write(data.get("response", "No response"))
            except Exception as e:
                st.error(f"Error: {e}")
