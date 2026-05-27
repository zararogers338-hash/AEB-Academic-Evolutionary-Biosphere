# -*- coding: utf-8 -*-
"""AEB 导出工具 / Export Utilities
支持: PNG, SVG, JSON, TXT, ZIP
"""

import json
import io
import zipfile
import datetime
import streamlit as st
from typing import Any, Dict


def export_json(data: Any, filename: str = "aeb_export.json"):
    """Provide JSON download button."""
    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    st.download_button(
        label=f"📥 {filename}",
        data=json_str.encode("utf-8"),
        file_name=filename,
        mime="application/json",
        key=f"dl_json_{filename}_{id(data) % 10**6}",
    )


def export_txt(text: str, filename: str = "aeb_export.txt"):
    """Provide TXT download button."""
    st.download_button(
        label=f"📥 {filename}",
        data=text.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        key=f"dl_txt_{filename}_{hash(text) % 10**6}",
    )


def export_csv(df, filename: str = "aeb_export.csv"):
    """Provide CSV download button."""
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 {filename}",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=f"dl_csv_{filename}",
    )


def export_zip(files_dict: Dict[str, str], zip_name: str = "aeb_export.zip"):
    """Create and provide ZIP download.
    files_dict: {"filename": "content_string"}
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files_dict.items():
            zf.writestr(fname, content.encode("utf-8") if isinstance(content, str) else content)
    buf.seek(0)
    st.download_button(
        label=f"📥 {zip_name}",
        data=buf.getvalue(),
        file_name=zip_name,
        mime="application/zip",
        key=f"dl_zip_{zip_name}",
    )


def render_export_panel(page_name: str, data: dict = None, text_content: str = "", df=None):
    """Render export buttons at bottom of page."""
    from utils.i18n import t
    st.markdown("---")
    cols = st.columns(4)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    with cols[0]:
        if data:
            export_json(data, f"aeb_{page_name}_{ts}.json")
    with cols[1]:
        if text_content:
            export_txt(text_content, f"aeb_{page_name}_{ts}.txt")
    with cols[2]:
        if df is not None and not df.empty:
            export_csv(df, f"aeb_{page_name}_{ts}.csv")
    with cols[3]:
        files = {}
        if data:
            files["data.json"] = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        if text_content:
            files["analysis.txt"] = text_content
        if df is not None and not df.empty:
            files["keywords.csv"] = df.to_csv(index=False)
        files["audit_log.txt"] = f"AEB Export - {page_name}\nTimestamp: {ts}\nFiles: {list(files.keys())}"
        if files:
            export_zip(files, f"aeb_{page_name}_{ts}.zip")
