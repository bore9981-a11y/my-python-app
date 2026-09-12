# -*- coding: utf-8 -*-
"""
3D 幻彩霓虹桌面时钟 · ICU 监护仪 (纯 Python 原生极简版)
============================================================
特点：
1. 【零第三方依赖】：纯 Python 标准库 (tkinter + winsound)，无需安装任何包；
2. 【完美支持 PyInstaller 打包】：可直接通过 timer.spec 编译为单个 exe；
3. 【系统级永久置顶】：root.attributes("-topmost", True)，绝不被浏览器遮挡；
4. 【1/4 屏幕精致小巧】：尺寸 360 x 210，默认悬浮停靠在屏幕右上角；
5. 【真实 ICU 机器音】：内置 1046.5Hz 脉搏蜂鸣，配有独立【声音开/关】按钮；
6. 【3D 霓虹幻彩与动态心电图】：夜空格栅背板 + 3D 阴影立体字 + 实时心电波形。
============================================================
"""

import tkinter as tk
import winsound
import threading
import datetime
import time

class NeonIcuClock:
    def __init__(self, root):
        self.root = root
        self.root.title("ICU_NEON_CLOCK")
        
        # 1. 永久置顶（Windows 系统原生支持，绝对不会被任何浏览器覆盖）
        self.root.attributes("-topmost", True)
        
        # 2. 1/4 屏幕小巧尺寸 (360 x 210)，自动停靠屏幕右上角
        self.width = 360
        self.height = 210
        sw = self.root.winfo_screenwidth()
        pos_x = max(20, sw - self.width - 30)
        pos_y = 30
        self.root.geometry(f"{self.width}x{self.height}+{pos_x}+{pos_y}")
        self.root.resizable(False, False)
        self.root.configure(bg="#12151a")
        
        # 状态变量
        self.sound_enabled = True
        self.is_24h = True
        self.last_sec = -1
        
        # 心电图动态参数
        self.ecg_x = 0
        self.ecg_points = []
        
        self.setup_ui()
        self.update_loop()
        self.ecg_loop()

    def setup_ui(self):
        # ---------------- 顶部控制栏 ----------------
        top_bar = tk.Frame(self.root, bg="#161a22", height=28)
        top_bar.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(6, 2))
        
        # 左侧 ICU 状态胶囊
        self.pulse_dot = tk.Label(top_bar, text="●", fg="#10b981", bg="#161a22", font=("Segoe UI", 8, "bold"))
        self.pulse_dot.pack(side=tk.LEFT, padx=(4, 2))
        
        icu_title = tk.Label(top_bar, text="ICU 60 BPM | 📌 置顶", fg="#6ee7b7", bg="#161a22", font=("Segoe UI", 8, "bold"))
        icu_title.pack(side=tk.LEFT)
        
        # 右侧：24H切换按钮
        self.btn_fmt = tk.Button(
            top_bar, text="24H", font=("Segoe UI", 7, "bold"),
            bg="#222734", fg="#94a3b8", activebackground="#2d3446", activeforeground="#ffffff",
            bd=0, padx=5, pady=1, cursor="hand2", command=self.toggle_format
        )
        self.btn_fmt.pack(side=tk.RIGHT, padx=2)

        # 右侧：试听按钮
        self.btn_test = tk.Button(
            top_bar, text="▶ 试听", font=("Segoe UI", 7, "bold"),
            bg="#222734", fg="#34d399", activebackground="#2d3446", activeforeground="#6ee7b7",
            bd=0, padx=5, pady=1, cursor="hand2", command=self.play_beep
        )
        self.btn_test.pack(side=tk.RIGHT, padx=2)

        # 右侧：声音总开关按钮
        self.btn_sound = tk.Button(
            top_bar, text="🔊 声音: 开", font=("Segoe UI", 7, "bold"),
            bg="#064e3b", fg="#6ee7b7", activebackground="#047857", activeforeground="#ffffff",
            bd=0, padx=6, pady=1, cursor="hand2", command=self.toggle_sound
        )
        self.btn_sound.pack(side=tk.RIGHT, padx=2)

        # ---------------- 中间时钟区域 (3D 霓虹立体字) ----------------
        self.clock_canvas = tk.Canvas(self.root, bg="#12151a", highlightthickness=0, height=88)
        self.clock_canvas.pack(fill=tk.X, padx=4, pady=0)

        # ---------------- ICU 心电动态示波区域 ----------------
        self.ecg_canvas = tk.Canvas(self.root, bg="#0b0e12", highlightthickness=1, highlightbackground="#222834", height=38)
        self.ecg_canvas.pack(fill=tk.X, padx=10, pady=(0, 4))

        # ---------------- 底部信息栏 (日期 / 星期 / 心率) ----------------
        bottom_bar = tk.Frame(self.root, bg="#12151a", height=24)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 6))

        self.lbl_date = tk.Label(bottom_bar, text="", fg="#94a3b8", bg="#12151a", font=("Segoe UI", 8, "bold"))
        self.lbl_date.pack(side=tk.LEFT)

        self.lbl_stat = tk.Label(bottom_bar, text="ECG NORMAL", fg="#34d399", bg="#12151a", font=("Segoe UI", 8, "bold"))
        self.lbl_stat.pack(side=tk.RIGHT)

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.btn_sound.config(text="🔊 声音: 开", bg="#064e3b", fg="#6ee7b7")
            self.play_beep()
        else:
            self.btn_sound.config(text="🔇 声音: 关", bg="#222734", fg="#94a3b8")

    def toggle_format(self):
        self.is_24h = not self.is_24h
        self.btn_fmt.config(text="24H" if self.is_24h else "12H")

    def play_beep(self):
        """医院 ICU 监护仪 1046.5Hz 标志性高频脉搏蜂鸣 (C6音)"""
        if not self.sound_enabled:
            return
        def _beep():
            try:
                # 1046Hz 蜂鸣 75毫秒，完全符合 ICU 心电监护仪标准
                winsound.Beep(1046, 75)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()

    def flash_pulse(self):
        """脉搏指示灯跳闪"""
        self.pulse_dot.config(fg="#ffffff")
        self.root.after(120, lambda: self.pulse_dot.config(fg="#10b981"))

    def draw_3d_text(self, h_str, m_str, s_str, ampm_str):
        self.clock_canvas.delete("all")
        cw = self.width
        
        # 绘制背景轻微格栅横纹
        for y in range(0, 88, 5):
            self.clock_canvas.create_line(0, y, cw, y, fill="#171b22", width=1)

        font_main = ("Arial Rounded MT Bold", 36, "bold")
        font_colon = ("Arial Rounded MT Bold", 30, "bold")
        font_ampm = ("Segoe UI", 9, "bold")

        base_y = 44
        cx = cw / 2
        
        # 整体居中排布
        h_x = cx - 110
        c1_x = cx - 55
        m_x = cx
        c2_x = cx + 55
        s_x = cx + 110

        # 色系搭配：时(琥珀橙) | 冒号1(玫红) | 分(幻彩紫) | 冒号2(青蓝) | 秒(天蓝)
        items = [
            (h_str, font_main, h_x, base_y, "#fb923c", "#7c2d12"),
            (":", font_colon, c1_x, base_y - 2, "#fb7185", "#881337"),
            (m_str, font_main, m_x, base_y, "#e879f9", "#701a75"),
            (":", font_colon, c2_x, base_y - 2, "#818cf8", "#312e81"),
            (s_str, font_main, s_x, base_y, "#38bdf8", "#0c4a6e"),
        ]

        for text, fnt, x, y, fg_color, shadow_color in items:
            # 3D 立体阴影
            self.clock_canvas.create_text(x + 2, y + 2, text=text, font=fnt, fill="#05070a")
            self.clock_canvas.create_text(x + 1, y + 2, text=text, font=fnt, fill=shadow_color)
            # 霓虹主表面
            self.clock_canvas.create_text(x, y, text=text, font=fnt, fill=fg_color)

        if not self.is_24h and ampm_str:
            self.clock_canvas.create_text(s_x + 36, base_y + 12, text=ampm_str, font=font_ampm, fill="#38bdf8")

    def update_loop(self):
        now = datetime.datetime.now()
        hours = now.hour
        ampm_str = ""
        if not self.is_24h:
            ampm_str = "PM" if hours >= 12 else "AM"
            hours = hours % 12
            if hours == 0:
                hours = 12

        h_str = f"{hours:02d}"
        m_str = f"{now.minute:02d}"
        s_str = f"{now.second:02d}"

        # 每秒刷新走字并触发 ICU 蜂鸣与脉搏闪烁
        if now.second != self.last_sec:
            self.last_sec = now.second
            self.play_beep()
            self.flash_pulse()
            self.trigger_heartbeat_wave()

        self.draw_3d_text(h_str, m_str, s_str, ampm_str)

        # 日期与星期显示
        weekdays_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekdays_en = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        w_idx = now.weekday()
        date_text = f"📅 {weekdays_cn[w_idx]} · {weekdays_en[w_idx]}  |  {now.strftime('%Y.%m.%d')}"
        self.lbl_date.config(text=date_text)

        self.root.after(100, self.update_loop)

    def trigger_heartbeat_wave(self):
        self.beat_active = True
        self.beat_step = 0

    def ecg_loop(self):
        """绘制动态绿色心电示波图"""
        w = self.width - 20
        h = 38
        mid_y = h / 2

        clear_x = (self.ecg_x + 8) % w
        self.ecg_canvas.create_rectangle(self.ecg_x, 0, clear_x, h, fill="#0b0e12", outline="")

        # 标准心电 P-Q-R-S-T 波形
        y_offset = 0
        if getattr(self, "beat_active", False):
            s = self.beat_step
            if s == 1:
                y_offset = -3      # P 波
            elif s == 2:
                y_offset = 1
            elif s == 3:
                y_offset = 3       # Q 谷
            elif s == 4:
                y_offset = -14     # R 尖峰
            elif s == 5:
                y_offset = 6       # S 谷
            elif s == 6:
                y_offset = -4      # T 波
            elif s >= 7:
                self.beat_active = False

            self.beat_step += 1

        cur_y = mid_y + y_offset

        if hasattr(self, "prev_x") and hasattr(self, "prev_y") and self.ecg_x > 0:
            self.ecg_canvas.create_line(self.prev_x, self.prev_y, self.ecg_x, cur_y, fill="#10b981", width=1.6)

        self.prev_x = self.ecg_x
        self.prev_y = cur_y

        self.ecg_x += 2
        if self.ecg_x >= w:
            self.ecg_x = 0
            self.prev_x = 0
            self.ecg_canvas.delete("all")
            for gx in range(0, w, 20):
                self.ecg_canvas.create_line(gx, 0, gx, h, fill="#121a1f", width=1)
            for gy in range(0, h, 10):
                self.ecg_canvas.create_line(0, gy, w, gy, fill="#121a1f", width=1)
            self.ecg_canvas.create_text(w - 55, 8, text="PULSE: 60  SpO2: 99%", fill="#38bdf8", font=("Segoe UI", 6, "bold"))

        self.root.after(25, self.ecg_loop)

def main():
    root = tk.Tk()
    app = NeonIcuClock(root)
    root.mainloop()

if __name__ == "__main__":
    main()
