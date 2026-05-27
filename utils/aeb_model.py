# -*- coding: utf-8 -*-
"""AEB AI模型后端管理 / AI Model Backend Manager
优先级: llama-cpp-python > Ollama > OpenAI Compatible
支持: 本地GGUF路径加载、Ollama管理、OpenAI/兼容API配置
"""

import time
import os
import streamlit as st
from typing import Optional, Generator


# --------------- Backend Availability Detection ---------------

def _check_llama_cpp() -> bool:
    try:
        from llama_cpp import Llama
        return True
    except Exception:
        return False

def _check_ollama() -> bool:
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False

def _check_openai() -> bool:
    try:
        import openai
        return True
    except Exception:
        return False


# --------------- Llama CPP Backend ---------------

class LlamaCppBackend:
    def __init__(self):
        self.model = None
        self.model_path = ""
        self.name = "llama-cpp-python"

    def load(self, model_path: str, n_ctx: int = 16384, n_gpu_layers: int = -1):
        from llama_cpp import Llama
        self.model_path = model_path
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )

    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        if not self.model:
            return "[ERROR] Model not loaded"
        result = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
        return result["choices"][0]["text"] if result.get("choices") else ""

    def generate_stream(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Generator:
        if not self.model:
            yield "[ERROR] Model not loaded"
            return
        for chunk in self.model(prompt, max_tokens=max_tokens, temperature=temperature, stream=True):
            delta = chunk.get("choices", [{}])[0].get("text", "")
            if delta:
                yield delta

    def health_check(self) -> dict:
        try:
            start = time.time()
            r = self.generate("Hi", max_tokens=5)
            latency = round((time.time() - start) * 1000, 1)
            return {"ok": True, "latency_ms": latency, "backend": self.name, "model": os.path.basename(self.model_path)}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": self.name}


# --------------- Ollama Backend ---------------

class OllamaBackend:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = ""
        self.name = "ollama"

    def list_models(self) -> list:
        try:
            import ollama
            resp = ollama.list()
            models = resp.get("models", []) if isinstance(resp, dict) else getattr(resp, "models", [])
            names = []
            for m in models:
                n = m.get("name", "") if isinstance(m, dict) else getattr(m, "model", getattr(m, "name", ""))
                if n:
                    names.append(n)
            return names
        except Exception:
            return []

    def pull_model(self, model_name: str, progress_bar=None):
        import ollama
        self.model_name = model_name
        try:
            stream = ollama.pull(model_name, stream=True)
            for chunk in stream:
                if progress_bar and hasattr(chunk, "completed") and hasattr(chunk, "total"):
                    if chunk.total and chunk.total > 0:
                        progress_bar.progress(min(chunk.completed / chunk.total, 1.0))
            if progress_bar:
                progress_bar.progress(1.0)
        except Exception as e:
            st.error(f"Pull failed: {e}")

    def load(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        import ollama
        resp = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        return resp.get("message", {}).get("content", "") if isinstance(resp, dict) else getattr(getattr(resp, "message", None), "content", "")

    def generate_stream(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Generator:
        import ollama
        stream = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, "num_predict": max_tokens},
            stream=True,
        )
        for chunk in stream:
            content = ""
            if isinstance(chunk, dict):
                content = chunk.get("message", {}).get("content", "")
            else:
                content = getattr(getattr(chunk, "message", None), "content", "")
            if content:
                yield content

    def health_check(self) -> dict:
        try:
            start = time.time()
            r = self.generate("Hi", max_tokens=5)
            latency = round((time.time() - start) * 1000, 1)
            return {"ok": True, "latency_ms": latency, "backend": self.name, "model": self.model_name}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": self.name}


# --------------- OpenAI Compatible Backend ---------------

class OpenAIBackend:
    def __init__(self, base_url: str = "", api_key: str = "sk-no-key", model: str = "gpt-4o-mini", timeout: int = 120, max_retries: int = 3):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = None
        self.name = "openai-compatible"

    def load(self, **kwargs):
        from openai import OpenAI
        self.base_url = kwargs.get("base_url", self.base_url)
        self.api_key = kwargs.get("api_key", self.api_key)
        self.model_name = kwargs.get("model", self.model_name)
        params = {"api_key": self.api_key, "timeout": self.timeout, "max_retries": self.max_retries}
        if self.base_url:
            params["base_url"] = self.base_url
        self.client = OpenAI(**params)

    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        if not self.client:
            self.load()
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    def generate_stream(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Generator:
        if not self.client:
            self.load()
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else ""
            if delta:
                yield delta

    def health_check(self) -> dict:
        try:
            start = time.time()
            r = self.generate("Hi", max_tokens=5)
            latency = round((time.time() - start) * 1000, 1)
            return {"ok": True, "latency_ms": latency, "backend": self.name, "model": self.model_name}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": self.name}


# --------------- Unified Model Manager ---------------

class AEBModelManager:
    """Manages backend priority and auto-fallback."""

    def __init__(self):
        self.backend = None
        self.backend_name = "none"
        self.is_degraded = True

    def auto_detect_and_load(self, config: dict) -> str:
        """Try backends in priority order. Returns backend name."""
        # 1) llama-cpp-python
        if config.get("llama_cpp", {}).get("enabled") and _check_llama_cpp():
            path = config["llama_cpp"].get("default_gguf_path", "")
            if path and os.path.isfile(path):
                try:
                    b = LlamaCppBackend()
                    b.load(path, n_ctx=config["llama_cpp"].get("n_ctx", 16384), n_gpu_layers=config["llama_cpp"].get("n_gpu_layers", -1))
                    self.backend = b
                    self.backend_name = "llama-cpp-python"
                    self.is_degraded = False
                    return self.backend_name
                except Exception:
                    pass

        # 2) Ollama
        if config.get("ollama", {}).get("enabled") and _check_ollama():
            try:
                b = OllamaBackend(config["ollama"].get("base_url", "http://localhost:11434"))
                models = b.list_models()
                target = config["ollama"].get("default_model", "")
                if target and target in models:
                    b.load(target)
                elif models:
                    b.load(models[0])
                else:
                    b.load(target)
                self.backend = b
                self.backend_name = "ollama"
                self.is_degraded = False
                return self.backend_name
            except Exception:
                pass

        # 3) OpenAI Compatible
        if config.get("openai_compatible", {}).get("enabled") and _check_openai():
            api_key = config["openai_compatible"].get("api_key", "")
            if api_key:
                try:
                    oc = config["openai_compatible"]
                    b = OpenAIBackend(
                        base_url=oc.get("base_url", ""),
                        api_key=api_key,
                        model=oc.get("model", "gpt-4o-mini"),
                        timeout=oc.get("timeout", 120),
                        max_retries=oc.get("max_retries", 3),
                    )
                    b.load()
                    self.backend = b
                    self.backend_name = "openai-compatible"
                    self.is_degraded = False
                    return self.backend_name
                except Exception:
                    pass

        self.backend_name = "none"
        self.is_degraded = True
        return self.backend_name

    def load_gguf(self, path: str, n_ctx: int = 16384, n_gpu_layers: int = -1):
        b = LlamaCppBackend()
        b.load(path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers)
        self.backend = b
        self.backend_name = "llama-cpp-python"
        self.is_degraded = False

    def load_ollama(self, model_name: str, base_url: str = "http://localhost:11434"):
        b = OllamaBackend(base_url)
        b.load(model_name)
        self.backend = b
        self.backend_name = "ollama"
        self.is_degraded = False

    def load_openai(self, base_url: str, api_key: str, model: str):
        b = OpenAIBackend(base_url=base_url, api_key=api_key, model=model)
        b.load()
        self.backend = b
        self.backend_name = "openai-compatible"
        self.is_degraded = False

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.backend:
            return "[No model loaded / 未加载模型]"
        try:
            return self.backend.generate(prompt, **kwargs)
        except Exception as e:
            return f"[AI Error: {e}]"

    def generate_stream(self, prompt: str, **kwargs) -> Generator:
        if not self.backend:
            yield "[No model loaded / 未加载模型]"
            return
        try:
            yield from self.backend.generate_stream(prompt, **kwargs)
        except Exception as e:
            yield f"[AI Error: {e}]"

    def health_check(self) -> dict:
        if not self.backend:
            return {"ok": False, "error": "No backend loaded", "backend": "none"}
        return self.backend.health_check()

    def get_status(self) -> dict:
        model_id = "N/A"
        if self.backend:
            model_id = getattr(self.backend, "model_name", "") or getattr(self.backend, "model_path", "") or "N/A"
            if isinstance(model_id, str) and os.sep in model_id:
                model_id = os.path.basename(model_id)
        return {
            "backend": self.backend_name,
            "model": model_id,
            "is_degraded": self.is_degraded,
            "loaded": self.backend is not None,
        }


def get_model_manager() -> AEBModelManager:
    """Get or create singleton model manager."""
    if "aeb_model_manager" not in st.session_state:
        st.session_state.aeb_model_manager = AEBModelManager()
    return st.session_state.aeb_model_manager


def render_model_panel(config: dict):
    """Render model configuration & status panel in sidebar."""
    from utils.i18n import t
    mgr = get_model_manager()
    status = mgr.get_status()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 " + t("model_panel"))

    # Status indicator
    if status["loaded"]:
        st.sidebar.success(f"✅ {status['backend']} — {status['model']}")
    else:
        st.sidebar.error("❌ 未连接模型 / No model connected")

    # Backend selector tabs
    backend_choice = st.sidebar.radio(
        "选择后端 / Select Backend",
        ["🧠 GGUF (本地)", "🦙 Ollama", "🌐 OpenAI / API"],
        key="backend_radio",
        horizontal=True,
    )

    # --- GGUF Local Path ---
    if backend_choice == "🧠 GGUF (本地)":
        if not _check_llama_cpp():
            st.sidebar.warning("⚠️ llama-cpp-python 未安装\n`pip install llama-cpp-python`")
        else:
            gguf_path = st.sidebar.text_input(
                "GGUF 文件路径 / GGUF File Path",
                value=st.session_state.get("gguf_path", config.get("llama_cpp", {}).get("default_gguf_path", "")),
                placeholder="C:/models/qwen2.5-7b-q4_k_m.gguf",
                key="gguf_path_input",
            )
            col1, col2 = st.sidebar.columns(2)
            n_ctx = col1.number_input("n_ctx", value=config.get("llama_cpp", {}).get("n_ctx", 16384), min_value=512, max_value=131072, step=1024, key="gguf_nctx")
            n_gpu = col2.number_input("GPU Layers", value=config.get("llama_cpp", {}).get("n_gpu_layers", -1), min_value=-1, max_value=200, key="gguf_ngpu")

            if st.sidebar.button("📂 加载 GGUF / Load GGUF", key="gguf_load_btn", use_container_width=True):
                if gguf_path and os.path.isfile(gguf_path):
                    with st.sidebar:
                        with st.spinner("加载模型中..."):
                            try:
                                mgr.load_gguf(gguf_path, n_ctx=int(n_ctx), n_gpu_layers=int(n_gpu))
                                st.session_state["gguf_path"] = gguf_path
                                st.sidebar.success(f"✅ Loaded: {os.path.basename(gguf_path)}")
                                st.rerun()
                            except Exception as e:
                                st.sidebar.error(f"❌ 加载失败: {e}")
                else:
                    st.sidebar.error("❌ 文件路径无效 / Invalid file path")

    # --- Ollama ---
    elif backend_choice == "🦙 Ollama":
        if not _check_ollama():
            st.sidebar.warning("⚠️ Ollama 未运行或未安装\n请先启动 Ollama: `ollama serve`")
        else:
            ollama_url = st.sidebar.text_input(
                "Ollama URL",
                value=st.session_state.get("ollama_url", config.get("ollama", {}).get("base_url", "http://localhost:11434")),
                key="ollama_url_input",
            )
            ob = OllamaBackend(ollama_url)
            models = ob.list_models()
            if models:
                sel = st.sidebar.selectbox("已有模型 / Available Models", models, key="ollama_model_sel")
                if st.sidebar.button("🔗 连接 / Connect", key="ollama_connect_btn", use_container_width=True):
                    mgr.load_ollama(sel, ollama_url)
                    st.session_state["ollama_url"] = ollama_url
                    st.sidebar.success(f"✅ Connected: {sel}")
                    st.rerun()
            else:
                st.sidebar.info("未发现模型 / No models found")

            # Pull new model
            with st.sidebar.expander("📥 拉取模型 / Pull Model"):
                pull_name = st.text_input("模型名称 / Model name", value="qwen2.5:7b", key="ollama_pull_input")
                if st.button("Pull", key="ollama_pull_btn"):
                    pb = st.progress(0)
                    ob.pull_model(pull_name, pb)
                    st.success(f"✅ Pulled: {pull_name}")

    # --- OpenAI / API ---
    elif backend_choice == "🌐 OpenAI / API":
        if not _check_openai():
            st.sidebar.warning("⚠️ openai 未安装\n`pip install openai`")
        else:
            oai_url = st.sidebar.text_input(
                "API Base URL",
                value=st.session_state.get("oai_url", config.get("openai_compatible", {}).get("base_url", "https://api.openai.com/v1")),
                key="oai_url_input",
            )
            oai_key = st.sidebar.text_input(
                "API Key",
                value=st.session_state.get("oai_key", config.get("openai_compatible", {}).get("api_key", "")),
                type="password",
                key="oai_key_input",
            )
            oai_model = st.sidebar.text_input(
                "Model Name",
                value=st.session_state.get("oai_model", config.get("openai_compatible", {}).get("model", "gpt-4o-mini")),
                key="oai_model_input",
            )

            st.sidebar.caption("💡 兼容: OpenAI / DeepSeek / 智谱 / Moonshot / 本地vLLM 等")

            if st.sidebar.button("🔗 连接 API / Connect", key="oai_connect_btn", use_container_width=True):
                if oai_key:
                    with st.sidebar:
                        with st.spinner("连接中..."):
                            try:
                                mgr.load_openai(oai_url, oai_key, oai_model)
                                st.session_state["oai_url"] = oai_url
                                st.session_state["oai_key"] = oai_key
                                st.session_state["oai_model"] = oai_model
                                st.sidebar.success(f"✅ Connected: {oai_model}")
                                st.rerun()
                            except Exception as e:
                                st.sidebar.error(f"❌ 连接失败: {e}")
                else:
                    st.sidebar.error("❌ 请输入 API Key")

    # Health check (always available)
    if status["loaded"]:
        if st.sidebar.button("🩺 " + t("health_check"), key="hc_btn", use_container_width=True):
            with st.sidebar, st.spinner(t("loading")):
                hc = mgr.health_check()
                if hc.get("ok"):
                    st.sidebar.success(f"✅ OK — {hc.get('latency_ms', '?')}ms")
                else:
                    st.sidebar.error(f"❌ {hc.get('error', 'Unknown')}")


def ai_analyze(prompt: str, stream_target=None) -> str:
    """Run AI analysis. If stream_target provided, stream to it."""
    mgr = get_model_manager()
    if stream_target is not None:
        full = ""
        for chunk in mgr.generate_stream(prompt):
            full += chunk
            stream_target.markdown(full)
        return full
    else:
        return mgr.generate(prompt)


def render_ai_panel(key_prefix: str = "main"):
    """Render AI analysis result panel."""
    from utils.i18n import t
    result_key = f"ai_result_{key_prefix}"
    if result_key not in st.session_state:
        st.session_state[result_key] = ""
    result = st.session_state.get(result_key, "")
    if result:
        st.markdown(f"### 🧬 {t('ai_analysis')}")
        st.markdown(result)
