# -*- coding: utf-8 -*-
"""
3D 雕塑石泥计算器 · 古琴音雅致版 (Streamlit 兼容 & 桌面独立窗口 双模版)
"""

import os
import sys
import subprocess
import tempfile
import webbrowser
import threading
import time
import base64

# --- 您的 HTML 代码保持不变 ---
HTML_CODE = """
<!-- 这里请保留您原来的完整 HTML 代码（包含 3D 浮雕、古琴音效等所有内容） -->
"""

def main():
    # 检查是否在 Streamlit 网页环境下运行
    is_streamlit = False
    try:
        import streamlit as st
        # 尝试调用一个仅在 streamlit 环境下有效的属性
        if st.runtime.exists():
            is_streamlit = True
    except ImportError:
        is_streamlit = False

    if is_streamlit:
        import streamlit as st
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 核心修复：使用 base64 编码 HTML 字符串，并用 st.iframe 渲染，彻底消除警告
        b64_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode()
        data_uri = f"data:text/html;base64,{b64_html}"
        
        # 渲染计算器，高度设为 650 以适配您的 1/4 屏幕设计
        st.iframe(data_uri, height=650, scrolling=False)
    else:
        # 如果是本地 Python 环境运行，执行您原有的独立窗口逻辑
        run_desktop_mode()

def run_desktop_mode():
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, "archi_3d_guqin_calc.html")
    profile_dir = os.path.join(temp_dir, "guqin_calc_profile")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)

    file_uri = f"file:///{html_file.replace(os.sep, '/')}"
    target_w, target_h = 380, 620

    # 1. 优先使用 pywebview
    try:
        import webview
        window = webview.create_window('3D 雕塑石泥计算器 · 古琴音', html=HTML_CODE, width=target_w, height=target_h)
        webview.start()
        return
    except Exception:
        pass

    # 2. Windows 原生独立小浮窗模式
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            pos_x, pos_y = max(0, (sw - target_w) // 2), max(0, (sh - target_h) // 2)
            
            cmd = f'start msedge --app="{file_uri}" --user-data-dir="{profile_dir}" --window-size={target_w},{target_h} --window-position={pos_x},{pos_y}'
            subprocess.Popen(cmd, shell=True)
            return
        except Exception:
            pass

    # 3. 降级方案
    webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
