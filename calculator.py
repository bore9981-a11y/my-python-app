# -*- coding: utf-8 -*-
import os
import streamlit as st
import base64

# --- 1. HTML_CODE 保持不变 ---
HTML_CODE = """
<!-- 这里粘贴你原本完整的 HTML 代码 -->
"""

def main():
    # 环境检测
    is_web = os.path.exists("/mount/src") or st.runtime.exists()

    if is_web:
        # --- 网页端渲染：避开 v1 警告的写法 ---
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 针对大体积 HTML 的优化处理
        # 1. 先进行 Base64 编码
        encoded_html = base64.b64encode(HTML_CODE.encode("utf-8")).decode("utf-8")
        
        # 2. 构建 Data URI，注意加入 charset 确保中文不空白
        data_uri = f"data:text/html;charset=utf-8;base64,{encoded_html}"
        
        # 3. 使用 st.iframe。注意：不要加任何 components.v1 前缀
        # 也不要加 scrolling=False。只给高度。
        st.iframe(data_uri, height=680)
        
        # 如果还是空白，说明你的 HTML 里的脚本可能尝试访问父窗口
        # 我们在下方加一个备用容器说明
        st.caption("若计算器未加载，请刷新页面或检查浏览器权限。")
            
    else:
        # --- 本地桌面模式 ---
        run_desktop_mode()

def run_desktop_mode():
    import tempfile
    import subprocess
    import sys
    
    t_dir = tempfile.gettempdir()
    h_file = os.path.join(t_dir, "guqin_calc.html")
    with open(h_file, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{h_file.replace(os.sep, '/')}"
    if sys.platform == "win32":
        # 桌面独立浮窗启动
        os.system(f'start msedge --app="{file_uri}" --window-size=380,620')
    else:
        import webbrowser
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
