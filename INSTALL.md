# Installation / 安装指南

## English

Recommended Python version: **3.9 to 3.11**.

```bash
git clone https://github.com/zararogers338-hash/AEB-Academic-Evolutionary-Biosphere.git
cd AEB-Academic-Evolutionary-Biosphere
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional AI backends:

```bash
pip install -r requirements-ai.txt
```

## 中文

推荐使用 **Python 3.9 到 3.11**。

```bash
git clone https://github.com/zararogers338-hash/AEB-Academic-Evolutionary-Biosphere.git
cd AEB-Academic-Evolutionary-Biosphere
python -m venv .venv
```

Windows：

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux / macOS：

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

可选 AI 后端：

```bash
pip install -r requirements-ai.txt
```

## Troubleshooting / 故障排除

If `llama-cpp-python` fails to install, skip it first and run the core visualization system. The AI backends are optional.

如果 `llama-cpp-python` 安装失败，可以先跳过它，先运行核心可视化系统。AI 后端是可选功能。
