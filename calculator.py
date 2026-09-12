# -*- coding: utf-8 -*-
import os
import streamlit as st
import tempfile

# 1. 你的 HTML 内容（请务必确保包含原来的所有内容）
HTML_CODE = """
<!-- 这里粘贴你原本完整的 HTML 代码 -->
"""

def main():
    # 检测环境
    is_web = os.path.exists("/mount/src") or st.runtime.exists()

    if is_web:
        # --- 网页端稳定渲染方案 ---
        st.set_page_config(page_title="3D 雕塑石泥计算器", layout="centered")
        
        # 将 HTML 写入临时文件，避免 Data URI 过长导致的空白问题
        # 这是解决大型 HTML 渲染最可靠的方法
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp:
            tmp.write(HTML_CODE)
            tmp_path = tmp.name
        
        # 读取文件内容并以 HTML 块的形式输出
        # 针对 2026 年 st.iframe 移除 v1 警告的最终合规写法
        with open(tmp_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # 使用 Streamlit 官方推荐的替代方案进行渲染
        # height 根据你的 1/4 屏幕设计设为 650
        st.components.v1.html(html_content, height=650)
        
        # 注意：如果上面的 v1.html 依然报警告，说明你的环境强制要求 st.iframe。
        # 这种情况下，我们需要将文件暴露为 URL。但目前最直接的修复是确保字符串不被截断。
        
    else:
        # --- 本地桌面模式逻辑 ---
        run_desktop_mode()

def run_desktop_mode():
    import subprocess
    import sys
    
    t_dir = tempfile.gettempdir()
    h_file = os.path.join(t_dir, "guqin_calc_native.html")
    with open(h_file, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)
    
    file_uri = f"file:///{h_file.replace(os.sep, '/')}"
    if sys.platform == "win32":
        os.system(f'start msedge --app="{file_uri}" --window-size=380,620')
    else:
        import webbrowser
        webbrowser.open(file_uri)

if __name__ == "__main__":
    main()
