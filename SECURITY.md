# Security Policy / 安全说明

## English

AEB processes user-uploaded academic documents locally inside the Streamlit session. Be careful with private, confidential, copyrighted, or sensitive documents.

Optional AI backends may send text to external services if you configure an OpenAI-compatible API. If you need privacy, use local GGUF or Ollama models and avoid external APIs.

Do not load untrusted local model files unless you understand the risks of the relevant inference engine.

## 中文

AEB 会在本地 Streamlit 会话中处理用户上传的学术文档。请谨慎处理私人、保密、受版权保护或敏感文档。

如果你配置 OpenAI-compatible API，可选 AI 后端可能会把文本发送到外部服务。如果你需要隐私，请优先使用本地 GGUF 或 Ollama 模型，并避免外部 API。

请不要随意加载不可信的本地模型文件，除非你理解对应推理引擎的安全风险。

## Reporting / 报告问题

Please open a GitHub issue for security concerns. Do not include private documents or secrets in public issues.
