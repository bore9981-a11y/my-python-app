# -*- coding: utf-8 -*-
import os
import base64
import streamlit as st

# --- 1. HTML 内容 (请确保保留你原本的完整代码) ---
HTML_CODE = """
<!-- 这里粘贴你原来的完整 HTML 代码 -->
"""

def main():
    # 环境检测：判断是否在网页端运行
    is_web = os.path.exists("/mount/src") or st.runtime.exists()

    if is_web:
        # --- 网页端渲染逻辑 ---
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 核心逻辑：将 HTML 转换为带编码的 Base64 字符串
        # 增加 charset=utf-8 声明是解决“空白页面”的关键
        try:
            b64_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode("utf-8")
            data_uri = f"data:text/html;charset=utf-8;base64,{b64_html}"
            
            # 使用最新的 st.iframe，不带 v1，不带 scrolling 参数
            st.iframe(data_uri, height=700)
        except Exception as e:
            st.error(f"代码解析失败: {e}")
            
    else:
        # --- 本地桌面模式逻辑 ---
        run_desktop_mode()

def run_desktop_mode():
    import tempfile
    import subprocess
    import sys
    
    temp_path = os.path.join(tempfile.gettempdir(), "guqin_calc.html")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{temp_path.replace(os.sep, '/')}"
    if sys.platform == "win32":
        # 桌面独立浮窗启动
        os.system(f'start msedge --app="{file_uri}" --window-size=380,620')
    else:
        import webbrowser
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
