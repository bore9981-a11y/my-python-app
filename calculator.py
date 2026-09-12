# -*- coding: utf-8 -*-
import os
import sys
import base64
import tempfile
import subprocess
import webbrowser

# 1. 你的 HTML 内容（请务必确保保留原来的所有 <style> 和 <script>）
HTML_CODE = """
<!-- 这里粘贴你原来的完整 HTML 代码 -->
"""

def main():
    # 环境检测：判断是否在 Streamlit 网页环境下运行
    in_streamlit = False
    try:
        import streamlit as st
        # 只要能检测到运行时的 metrics 或者是 Streamlit Cloud 的特定路径
        if st.runtime.exists() or os.path.exists("/mount/src"):
            in_streamlit = True
    except (ImportError, Exception):
        in_streamlit = False

    if in_streamlit:
        import streamlit as st
        # 网页端渲染逻辑
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 核心修复：将 HTML 转换为 Data URI 格式
        b64_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode()
        data_uri = f"data:text/html;base64,{b64_html}"
        
        # 修复点：移除了会导致 TypeError 的 scrolling 参数，仅保留核心参数
        st.iframe(data_uri, height=650)
        
        # 添加一个底部的温馨提示
        st.caption("注：当前为网页兼容模式。如需独立桌面小窗口，请在本地运行 python 脚本。")
    else:
        # 本地桌面模式逻辑
        run_desktop_native()

def run_desktop_native():
    """保留你原本的桌面端 msedge --app 启动逻辑"""
    temp_dir = tempfile.gettempdir()
    html_path = os.path.join(temp_dir, "guqin_calc.html")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{html_path.replace(os.sep, '/')}"
    target_w, target_h = 380, 620
    
    if sys.platform == "win32":
        try:
            # 尝试使用独立应用模式启动 Edge
            subprocess.Popen(
                f'start msedge --app="{file_uri}" --window-size={target_w},{target_h}', 
                shell=True
            )
        except Exception:
            webbrowser.open(file_uri)
    else:
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
