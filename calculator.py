# -*- coding: utf-8 -*-
import os
import sys
import base64
import streamlit as st

# --- 1. HTML_CODE 保持不变，请确保包含你原来的完整代码 ---
HTML_CODE = """
<!-- 这里粘贴你原本的完整 HTML 代码 -->
"""

def main():
    # 检查是否在 Streamlit 网页环境下运行
    # 判断标准：是否存在 Streamlit Cloud 路径或运行时环境
    is_web = os.path.exists("/mount/src") or st.runtime.exists()

    if is_web:
        # --- 网页渲染模式 ---
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 将 HTML 转换为 base64
        b64_content = base64.b64encode(HTML_CODE.encode("utf-8")).decode()
        data_uri = f"data:text/html;base64,{b64_content}"
        
        # 【核心修复】：去掉了引发报错的 scrolling 参数，只保留 height
        st.iframe(data_uri, height=650)
        
    else:
        # --- 本地桌面模式 ---
        run_local_desktop()

def run_local_desktop():
    import tempfile
    import subprocess
    
    temp_path = os.path.join(tempfile.gettempdir(), "guqin_calc.html")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_url = f"file:///{temp_path.replace(os.sep, '/')}"
    
    if sys.platform == "win32":
        # 尝试以桌面应用模式启动
        os.system(f'start msedge --app="{file_url}" --window-size=380,620')
    else:
        import webbrowser
        webbrowser.open(file_url)

if __name__ == "__main__":
    main()
