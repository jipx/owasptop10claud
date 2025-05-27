

# OWASP Assistant with Claude via Amazon Bedrock (Inline Lambda + API Gateway)

![Streamlit Cloud](https://img.shields.io/badge/Deployed%20on-Streamlit%20Cloud-blueviolet)
![AWS](https://img.shields.io/badge/Powered%20by-Amazon%20Bedrock-orange)
![License](https://img.shields.io/github/license/your-username/owasp-bedrock-assistant)

This project deploys a public REST API using **Amazon API Gateway** and **AWS Lambda**, which forwards prompts to **Claude via Amazon Bedrock** and returns natural-language explanations for OWASP Top 10 vulnerabilities.

---

## ✅ Architecture

```
[Streamlit App or Postman]
       |
       v
[API Gateway /prod/ask]
       |
       v
[AWS Lambda (Inline Python)]
       |
       v
[Amazon Bedrock (Claude)]
```

---

## ✅ Use Cases

- Educational OWASP security assistant
- API-first integration with Claude (via Bedrock)
- Serverless deployment via CloudFormation
- Secure, public, cost-efficient design

---

## ✅ How to Deploy

### 1. Download and Apply CloudFormation

```bash
aws cloudformation deploy   --template-file owasp_claude_inline.yaml   --stack-name owasp-assistant-inline   --capabilities CAPABILITY_NAMED_IAM
```

### 2. Fix Common Error

> If you see: `"Unable to import module 'lambda_function'"`

You must ensure:

```yaml
Handler: index.lambda_handler
```

Because CloudFormation inline Lambda treats the code as `index.py` by default.

---

## ✅ API Usage

**Endpoint:**

```
POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/ask
```

**Headers:**

```http
Content-Type: application/json
```

**Body:**

```json
{
  "prompt": "Explain SQL Injection with an example"
}
```

**Response:**

```json
{
  "response": "Claude-generated explanation here..."
}
```

---

## ✅ Supported Claude Models

| Model               | Model ID                                             | Notes                                                                 |
|---------------------|------------------------------------------------------|-----------------------------------------------------------------------|
| Claude v2           | `anthropic.claude-v2`                                | ✅ Supports direct invocation                                          |
| Claude 3.5 Sonnet   | `anthropic.claude-3-sonnet-20240229-v1:0`            | ❗ Requires inference profile (provisioned throughput only)            |

---

## ⚠️ Using Claude 3.5 Sonnet

Claude 3.5 Sonnet requires a **provisioned throughput** configuration:

1. Go to **Amazon Bedrock Console** → *Provisioned throughput*
2. Create a **Claude 3 Sonnet** configuration
3. Use the **ARN** of the provisioned model as `modelId` in your code:

```python
modelId="arn:aws:bedrock:<region>:<account-id>:provisioned-model/<inference-profile-id>"
```

If you don’t have a provisioned profile, use `anthropic.claude-v2` as a fallback.

---

## ✅ Secrets Setup for Bedrock (if calling directly)

In `.streamlit/secrets.toml` or environment variables:

```toml
AWS_ACCESS_KEY_ID = "your-key"
AWS_SECRET_ACCESS_KEY = "your-secret"
BEDROCK_REGION = "us-east-1"
```

---

## ✅ Troubleshooting

| Error                                                                                     | Fix                                                                 |
|-------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `Unable to import module 'lambda_function'`                                              | Use `Handler: index.lambda_handler` in inline Lambda                |
| 403 Forbidden from API Gateway                                                            | Ensure Lambda permission added + API Gateway deployed               |
| `ValidationException: Invocation of model ID ... with on-demand throughput isn’t supported` | Use a provisioned throughput ARN or fallback to Claude v2           |

---

## ✅ License

MIT License

Built using:
- Amazon API Gateway
- AWS Lambda
- Amazon Bedrock Claude
- Streamlit
