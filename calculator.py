# -*- coding: utf-8 -*-
import os
import base64
import streamlit as st
import streamlit.components.v1 as components

# --- 1. 你的 HTML 内容（请确保保留原来的完整代码） ---
HTML_CODE = """
<!-- 这里粘贴你原来的完整 HTML 代码 -->
"""

def main():
    # 检测是否在网页环境
    if os.path.exists("/mount/src") or st.runtime.exists():
        render_web_mode()
    else:
        run_desktop_mode()

def render_web_mode():
    st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")

    # 方案：将 HTML 包装成一个可以直接渲染的 Data URI
    # 如果 HTML 太大导致空白，我们加上 utf-8 声明和必要的转义
    try:
        encoded_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode("utf-8")
        data_uri = f"data:text/html;charset=utf-8;base64,{encoded_html}"
        
        # 使用 components.iframe (这是目前最稳定的嵌入方式)
        # 注意：height 必须足够大以容纳你的计算器
        components.iframe(data_uri, height=700)
        
    except Exception as e:
        st.error(f"渲染失败: {e}")

def run_desktop_mode():
    import tempfile
    import subprocess
    import sys
    
    temp_path = os.path.join(tempfile.gettempdir(), "guqin_calc.html")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{temp_path.replace(os.sep, '/')}"
    if sys.platform == "win32":
        os.system(f'start msedge --app="{file_uri}" --window-size=380,620')
    else:
        import webbrowser
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
