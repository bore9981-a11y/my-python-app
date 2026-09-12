# -*- coding: utf-8 -*-
import os
import streamlit as st
import base64

# --- HTML 保持不变 (为了简洁，这里省略你提供的长字符串，实际使用时请保留完整内容) ---
HTML_CODE = """
<!-- 这里粘贴你原来的完整 HTML_CODE 内容 -->
"""

def main():
    # 检查是否在 Streamlit 环境中运行
    # 如果用户通过 streamlit run calculator.py 启动
    try:
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 1. 将 HTML 转换为 base64 以便 st.iframe 调用
        b64_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode()
        data_uri = f"data:text/html;base64,{b64_html}"

        # 2. 使用新的 st.iframe 替代弃用的 st.components.v1.html
        # 注意：Streamlit 网页端无法像桌面端那样精准控制窗口 380x620 悬浮，
        # 但我们可以控制组件的显示高度。
        st.iframe(data_uri, height=650, scrolling=False)
        
        st.write("注：当前作为网页组件运行。若需独立桌面浮窗，请直接使用 Python 运行此脚本。")

    except Exception:
        # 如果不是在 Streamlit 中，则保留你原来的桌面启动逻辑
        run_as_desktop()

def run_as_desktop():
    # 这里放你原来的桌面启动逻辑（msedge --app 或 pywebview）
    import tempfile
    import subprocess
    import sys
    
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, "archi_3d_guqin_calc.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{html_file.replace(os.sep, '/')}"
    target_w, target_h = 380, 620
    
    if sys.platform == "win32":
        # 你原本的 msedge --app 启动代码...
        os.system(f'start msedge --app="{file_uri}" --window-size={target_w},{target_h}')
    else:
        import webbrowser
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
