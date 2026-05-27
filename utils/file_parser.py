# -*- coding: utf-8 -*-
"""AEB 文件解析模块 / Robust File Parser Module
支持: txt, pdf, md, docx, doc, json, jsonl, csv, tsv, xlsx, xls, html, xml, yaml, yml
"""

import io
import json
from typing import Dict, Any

CHUNK_SIZE = 1024 * 1024  # 1MB chunks for large files


def parse_file(uploaded_file) -> Dict[str, Any]:
    """Parse an uploaded file and return unified result dict.
    Returns: {"text": str, "success": bool, "format": str, "error": str}
    """
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    ext = name.rsplit(".", 1)[-1] if "." in name else "txt"

    try:
        if ext == "pdf":
            return _parse_pdf(data, name)
        elif ext in ("doc", "docx"):
            return _parse_docx(data, name)
        elif ext in ("xlsx", "xls"):
            return _parse_excel(data, name)
        elif ext in ("json", "jsonl"):
            return _parse_json(data, name, ext)
        elif ext in ("csv", "tsv"):
            return _parse_csv(data, name, ext)
        elif ext in ("html", "htm", "xml"):
            return _parse_html_xml(data, name)
        elif ext in ("yaml", "yml"):
            return _parse_yaml(data, name)
        else:
            # txt, md, markdown, etc.
            return _parse_text(data, name)
    except Exception as e:
        # Ultimate fallback: try as raw text
        return _fallback_text(data, name, str(e))


def _detect_encoding(data: bytes) -> str:
    """Detect encoding with fallback chain."""
    try:
        import chardet
        det = chardet.detect(data[:10000])
        enc = det.get("encoding", "utf-8") or "utf-8"
        return enc
    except Exception:
        pass
    for enc in ("utf-8", "gbk", "gb2312", "latin1", "ascii"):
        try:
            data.decode(enc)
            return enc
        except Exception:
            continue
    return "utf-8"


def _decode_bytes(data: bytes) -> str:
    """Decode bytes to string with fallback."""
    enc = _detect_encoding(data)
    try:
        return data.decode(enc)
    except Exception:
        return data.decode("utf-8", errors="ignore")


def _parse_text(data: bytes, name: str) -> Dict:
    text = _decode_bytes(data)
    return {"text": text, "success": True, "format": "text", "error": ""}


def _parse_pdf(data: bytes, name: str) -> Dict:
    text = ""
    # Try PyMuPDF first
    try:
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        if text.strip():
            return {"text": text, "success": True, "format": "pdf/pymupdf", "error": ""}
    except Exception:
        pass
    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        if text.strip():
            return {"text": text, "success": True, "format": "pdf/pdfplumber", "error": ""}
    except Exception:
        pass
    # Fallback raw
    return _fallback_text(data, name, "PDF parsers unavailable")


def _parse_docx(data: bytes, name: str) -> Dict:
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
        return {"text": text, "success": True, "format": "docx", "error": ""}
    except Exception as e:
        return _fallback_text(data, name, f"docx parse error: {e}")


def _parse_excel(data: bytes, name: str) -> Dict:
    try:
        import pandas as pd
        df = pd.read_excel(io.BytesIO(data), engine="openpyxl")
        text = df.to_string(index=False)
        return {"text": text, "success": True, "format": "excel", "error": ""}
    except Exception as e:
        return _fallback_text(data, name, f"excel parse error: {e}")


def _parse_json(data: bytes, name: str, ext: str) -> Dict:
    raw = _decode_bytes(data)
    try:
        if ext == "jsonl":
            lines = [json.loads(line) for line in raw.strip().split("\n") if line.strip()]
            text = "\n".join(json.dumps(item, ensure_ascii=False, indent=1) for item in lines)
        else:
            obj = json.loads(raw)
            text = json.dumps(obj, ensure_ascii=False, indent=2)
        return {"text": text, "success": True, "format": ext, "error": ""}
    except Exception as e:
        return {"text": raw, "success": True, "format": "text_fallback", "error": str(e)}


def _parse_csv(data: bytes, name: str, ext: str) -> Dict:
    raw = _decode_bytes(data)
    try:
        import pandas as pd
        sep = "\t" if ext == "tsv" else ","
        df = pd.read_csv(io.StringIO(raw), sep=sep)
        text = df.to_string(index=False)
        return {"text": text, "success": True, "format": ext, "error": ""}
    except Exception:
        return {"text": raw, "success": True, "format": "text_fallback", "error": ""}


def _parse_html_xml(data: bytes, name: str) -> Dict:
    raw = _decode_bytes(data)
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw, "lxml" if name.endswith("xml") else "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return {"text": text, "success": True, "format": "html/xml", "error": ""}
    except Exception:
        # Strip tags manually
        import re
        text = re.sub(r"<[^>]+>", " ", raw)
        return {"text": text, "success": True, "format": "html_stripped", "error": ""}


def _parse_yaml(data: bytes, name: str) -> Dict:
    raw = _decode_bytes(data)
    try:
        import yaml
        obj = yaml.safe_load(raw)
        text = yaml.dump(obj, allow_unicode=True, default_flow_style=False)
        return {"text": text, "success": True, "format": "yaml", "error": ""}
    except Exception:
        return {"text": raw, "success": True, "format": "text_fallback", "error": ""}


def _fallback_text(data: bytes, name: str, original_error: str) -> Dict:
    """Ultimate fallback: extract as much readable text as possible."""
    text = data.decode("utf-8", errors="ignore")
    # Filter out non-printable characters
    text = "".join(c for c in text if c.isprintable() or c in "\n\r\t")
    return {"text": text, "success": bool(text.strip()), "format": "raw_fallback", "error": original_error}


def parse_multiple_files(uploaded_files, progress_callback=None) -> list:
    """Parse multiple uploaded files. Returns list of result dicts."""
    results = []
    total = len(uploaded_files)
    for i, f in enumerate(uploaded_files):
        result = parse_file(f)
        result["filename"] = f.name
        results.append(result)
        if progress_callback:
            progress_callback((i + 1) / total, f.name)
    return results
