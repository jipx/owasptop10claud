
# OWASP Top 10 Assistant with Claude via Amazon Bedrock

![Streamlit Cloud](https://img.shields.io/badge/Deployed%20on-Streamlit%20Cloud-blueviolet)
![AWS](https://img.shields.io/badge/Powered%20by-Amazon%20Bedrock-orange)
![License](https://img.shields.io/github/license/your-username/owasp-bedrock-assistant)

This project is a **Streamlit web app** that helps users explore OWASP Top 10 vulnerabilities with natural language explanations from Claude (Anthropic) via Amazon Bedrock.

---

## 📸 Preview

![App Screenshot](https://user-images.githubusercontent.com/your-id/owasp-assistant-demo.png)

---

## 🚀 Live App

[Launch OWASP Assistant](https://your-app-name.streamlit.app)

---

## ⚙️ Architecture

```
[Streamlit App]
      |
      v
[API Gateway + API Key]
      |
      v
[AWS Lambda Function]
      |
      v
[Amazon Bedrock (Claude)]
```

---

## 🛠️ How to Deploy

### 1. Deploy the Backend (API Gateway + Lambda + Claude)
Use this CloudFormation template:

```bash
aws cloudformation deploy \
  --template-file owasp_claude_api_throttling_export.yaml \
  --stack-name owasp-bedrock-api \
  --capabilities CAPABILITY_NAMED_IAM
```

Then go to the **CloudFormation Outputs tab** and copy the exported `ClaudeApiKey`.

---

### 2. Run the Streamlit Frontend

```bash
streamlit run app.py
```

When prompted, enter your API URL and provide this in headers:

```python
headers = {
    "x-api-key": "YOUR_EXPORTED_API_KEY"
}
```

---

### 3. Secrets (in `.streamlit/secrets.toml` or Streamlit Cloud)

```toml
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "your-secret"
BEDROCK_REGION = "us-east-1"
```

---

## 🧠 OWASP Top 10 Topics Included

- Broken Access Control
- Cryptographic Failures
- Injection
- Insecure Design
- Security Misconfiguration
- Vulnerable and Outdated Components
- Identification and Authentication Failures
- Software and Data Integrity Failures
- Security Logging and Monitoring Failures
- Server Side Request Forgery (SSRF)

---

## 📝 License

MIT License
