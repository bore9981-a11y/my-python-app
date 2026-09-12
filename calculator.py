# -*- coding: utf-8 -*-
"""
3D 雕塑石泥计算器 · 古琴音雅致版 (Python 原生桌面 1/4 屏幕独立窗口版)
========================================================================
更新调整：
1. 窗口尺寸设为标准的「屏幕 1/4 大小」桌面浮窗（380 x 620），小巧精致、协调居中。
2. 彻底解决窗口被系统自动最大化/铺满屏幕的问题：
   - 启用独立隔离配置（--user-data-dir），避免继承此前浏览器的全屏或大窗口状态；
   - 引入 Windows 原生 ctypes 窗口监控，确保窗口启动即保持 1/4 浮窗，绝不铺满屏幕；
3. 界面完全浑然一体：窗口与计算器石板 1:1 无缝重合，无黑边、无留白。
4. 屏幕三行完整 3D 浮雕与古琴音效完全保留，结果绝无遮挡。
========================================================================
"""

import os
import sys
import subprocess
import tempfile
import webbrowser
import threading
import time

HTML_CODE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>3D 雕塑石泥计算器 · 古琴音</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* 彻底消除多层嵌套：窗口即计算器本体，浑然一体的灰泥石板表面 */
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }

    body {
      background: radial-gradient(circle at 40% 30%, #e2e7e1 0%, #d1d7d0 60%, #c4cac2 100%);
      box-sizing: border-box;
      padding: 14px 16px 14px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-family: 'Arial Rounded MT Bold', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      user-select: none;
      -webkit-user-select: none;
    }

    /* 顶栏 3D 浮雕标题 */
    .text-3d-header {
      font-weight: 900;
      color: #92998f;
      letter-spacing: 0.5px;
      text-shadow:
        -1px -1px 0 rgba(255, 255, 255, 0.9),
        1px 1px 0 #737a70,
        2px 2px 1px rgba(40, 50, 43, 0.25);
    }

    /* 雕刻深槽托盘大屏幕 (高度充裕，彻底避免遮挡) */
    .stone-screen-tray {
      background: linear-gradient(180deg, #b6bcb3 0%, #c2c8bf 100%);
      box-shadow: 
        inset 3px 4px 10px rgba(45, 55, 47, 0.35),
        inset -2px -2px 4px rgba(255, 255, 255, 0.65),
        0 1px 2px rgba(255, 255, 255, 0.7);
      border: 1px solid rgba(90, 100, 92, 0.35);
      border-radius: 16px;
      padding: 10px 12px 8px 12px;
      min-height: 154px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-sizing: border-box;
      overflow: visible;
    }

    /* 历史记录芯片 3D 浮雕块 (第二行) */
    .history-chip {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(195, 201, 193, 0.35) 100%);
      border: 1px solid rgba(255, 255, 255, 0.7);
      border-radius: 7px;
      box-shadow: 
        1px 1px 0 #9ca399,
        2px 2px 3px rgba(40, 50, 43, 0.2);
      padding: 2px 8px;
      margin-bottom: 3px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: transform 0.1s ease, box-shadow 0.1s ease;
    }
    .history-chip:hover {
      transform: translate(-1px, -1px);
      box-shadow: 2px 2px 0 #9ca399, 3px 3px 5px rgba(40, 50, 43, 0.25);
    }
    .history-chip:active {
      transform: translate(1px, 1px);
      box-shadow: 1px 1px 1px rgba(40, 50, 43, 0.2);
    }

    .history-expr-3d {
      color: #7b8278;
      font-weight: 700;
      font-size: 11px;
      text-shadow: -0.5px -0.5px 0 rgba(255, 255, 255, 0.8), 0.8px 0.8px 0 #5c6359;
    }

    .history-val-3d {
      font-weight: 900;
      color: #636b60;
      font-size: 12px;
      text-shadow: -1px -1px 0 rgba(255, 255, 255, 0.9), 1px 1px 0 #7b8278, 2px 2px 1px rgba(40, 50, 43, 0.28);
    }

    /* 主输出结果区域 (第三行：空间充分，大号 3D 数字阴影绝无遮挡) */
    .main-display-stage {
      min-height: 50px;
      padding: 2px;
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      overflow: visible;
    }

    .text-3d-sculpt {
      font-weight: 900;
      color: #bcc3ba;
      letter-spacing: 1px;
      text-shadow:
        -1.5px -1.5px 1px rgba(255, 255, 255, 0.95),
        1.5px 1.5px 0 #90978d,
        3px 3px 0 #7e857b,
        4.5px 4.5px 0 #6d746a,
        6px 6px 0 #5e655c,
        7px 7px 0 #4f564d,
        8px 9px 3px rgba(35, 45, 38, 0.45),
        10px 12px 10px rgba(35, 45, 38, 0.25);
      display: inline-block;
      transform-origin: right center;
      transition: transform 0.08s ease;
      line-height: 1.1;
    }

    .screen-hit {
      animation: stoneTextBounce 0.2s ease-out;
    }
    @keyframes stoneTextBounce {
      0% { transform: scale(1.05) translate(-1px, -1px); }
      100% { transform: scale(1) translate(0, 0); }
    }

    .stone-scroll::-webkit-scrollbar { width: 4px; }
    .stone-scroll::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); border-radius: 2px; }
    .stone-scroll::-webkit-scrollbar-thumb { background: #8e958b; border-radius: 2px; }

    /* 按键 3D 实体挤出石块 */
    .btn-3d-block {
      position: relative;
      cursor: pointer;
      border-radius: 0.85rem;
      font-weight: 900;
      box-shadow: 
        1px 1px 0 #9ca399,
        2px 2px 0 #8a9187,
        3px 3px 0 #787f75,
        4px 4px 0 #686f65,
        5px 5px 0 #585f55,
        6px 8px 12px rgba(45, 55, 48, 0.28);
      transition: transform 0.07s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.07s cubic-bezier(0.2, 0, 0, 1);
      display: flex;
      align-items: center;
      justify-content: center;
      height: 50px;
    }

    .btn-3d-block::before {
      content: "";
      position: absolute;
      inset: 1px;
      border-radius: 0.8rem;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0) 50%);
      pointer-events: none;
    }

    .btn-3d-block:hover {
      transform: translate(-1px, -1px);
      box-shadow: 
        1px 1px 0 #9ca399,
        2px 2px 0 #8a9187,
        3px 3px 0 #787f75,
        4px 4px 0 #686f65,
        5px 5px 0 #585f55,
        6px 6px 0 #4a5147,
        7px 10px 16px rgba(45, 55, 48, 0.35);
    }

    .btn-3d-block:active, .btn-3d-block.is-pressed {
      transform: translate(4px, 4px) !important;
      box-shadow: 1px 1px 0 #585f55, 2px 2px 4px rgba(45, 55, 48, 0.3) !important;
    }

    .btn-font-3d {
      font-weight: 900;
      line-height: 1;
      display: inline-block;
      pointer-events: none;
    }

    .btn-clay-num {
      background: linear-gradient(145deg, #d8ddd6 0%, #c6cdc4 100%);
      border: 1px solid rgba(255, 255, 255, 0.8);
    }
    .btn-clay-num .btn-font-3d {
      color: #9ea59b;
      text-shadow: 
        -1.5px -1.5px 0 rgba(255, 255, 255, 0.95),
        1.5px 1.5px 0 #7a8177,
        3px 3px 0 #5f665c,
        4.5px 4.5px 3px rgba(40, 50, 43, 0.42);
    }

    .btn-clay-op {
      background: linear-gradient(145deg, #ceb8a8 0%, #b89f8e 100%);
      border: 1px solid rgba(255, 255, 255, 0.7);
      box-shadow: 
        1px 1px 0 #947e70, 2px 2px 0 #816b5d, 3px 3px 0 #705b4e,
        4px 4px 0 #604d40, 5px 5px 0 #503e33, 6px 8px 12px rgba(60, 45, 35, 0.28);
    }
    .btn-clay-op:hover {
      box-shadow: 
        1px 1px 0 #947e70, 2px 2px 0 #816b5d, 3px 3px 0 #705b4e,
        4px 4px 0 #604d40, 5px 5px 0 #503e33, 6px 6px 0 #423228,
        7px 10px 16px rgba(60, 45, 35, 0.35);
    }
    .btn-clay-op:active, .btn-clay-op.is-pressed {
      box-shadow: 1px 1px 0 #503e33, 2px 2px 4px rgba(60, 45, 35, 0.3) !important;
    }
    .btn-clay-op .btn-font-3d {
      color: #8c7363;
      text-shadow: 
        -1.5px -1.5px 0 rgba(255, 255, 255, 0.9),
        1.5px 1.5px 0 #6b5647,
        3px 3px 0 #4f3d30,
        4.5px 4.5px 3px rgba(50, 35, 25, 0.45);
    }

    .btn-clay-fn {
      background: linear-gradient(145deg, #bfc6be 0%, #abb3aa 100%);
      border: 1px solid rgba(255, 255, 255, 0.6);
    }
    .btn-clay-fn .btn-font-3d {
      color: #7b8378;
      text-shadow: 
        -1.5px -1.5px 0 rgba(255, 255, 255, 0.9),
        1.5px 1.5px 0 #5d645a,
        3px 3px 0 #444a42,
        4.5px 4.5px 3px rgba(40, 50, 43, 0.42);
    }

    .btn-clay-eq {
      background: linear-gradient(145deg, #a7b5a5 0%, #8b9c89 100%);
      border: 1px solid rgba(255, 255, 255, 0.7);
      box-shadow: 
        1px 1px 0 #6e7f6c, 2px 2px 0 #5d6d5b, 3px 3px 0 #4e5d4c,
        4px 4px 0 #404d3e, 5px 5px 0 #333e31, 6px 8px 12px rgba(35, 50, 38, 0.35);
    }
    .btn-clay-eq:hover {
      box-shadow: 
        1px 1px 0 #6e7f6c, 2px 2px 0 #5d6d5b, 3px 3px 0 #4e5d4c,
        4px 4px 0 #404d3e, 5px 5px 0 #333e31, 6px 6px 0 #283226,
        7px 10px 16px rgba(35, 50, 38, 0.42);
    }
    .btn-clay-eq:active, .btn-clay-eq.is-pressed {
      box-shadow: 1px 1px 0 #333e31, 2px 2px 4px rgba(35, 50, 38, 0.3) !important;
    }
    .btn-clay-eq .btn-font-3d {
      color: #61735f;
      text-shadow: 
        -1.5px -1.5px 0 rgba(255, 255, 255, 0.9),
        1.5px 1.5px 0 #465544,
        3px 3px 0 #303d2f,
        4.5px 4.5px 3px rgba(25, 40, 28, 0.5);
    }
  </style>
</head>
<body>

  <!-- 顶部状态栏 -->
  <div class="flex items-center justify-between px-1 text-xs text-[#6e756b]">
    <div class="flex items-center gap-1.5 font-bold tracking-widest text-[11px] uppercase text-3d-header">
      <span class="inline-block w-2.5 h-2.5 rounded-full bg-[#8b9c89] shadow-inner"></span>
      <span>ARCHI · 3D GUQIN</span>
    </div>
    <div>
      <button id="soundToggle" class="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#c9cfc6] hover:bg-[#bcc3b9] text-[11px] text-[#484f45] border border-white/80 transition shadow-sm font-semibold">
        <span id="soundIcon">🪕</span>
        <span id="soundLabel">古琴开</span>
      </button>
    </div>
  </div>

  <!-- 凹陷深雕大屏幕 (完整 3D 浮雕结构：无遮挡) -->
  <div class="stone-screen-tray my-1.5">
    <!-- 第一行：3D 浮雕标题 + 3D 清空按键 -->
    <div class="flex items-center justify-between pb-1 border-b border-[#a3a9a0]/60 text-[11px]">
      <div class="flex items-center gap-1.5 text-3d-header">
        <span>📜</span>
        <span>历史古卷 · ARCHIVE</span>
      </div>
      <button id="clearHistoryBtn" class="px-2 py-0.5 rounded-md bg-[#b8beb5] hover:bg-[#aeb4ab] text-[#545b51] font-bold text-[10px] shadow-[1px_1px_0_#8e958b] active:translate-x-[1px] active:translate-y-[1px] border border-white/70 transition">
        🗑️ 清空
      </button>
    </div>

    <!-- 第二行：3D 浮雕古卷记录条目列表 -->
    <div id="historyScrollBox" class="stone-scroll flex-1 overflow-y-auto max-h-[66px] my-1 pr-1 space-y-1">
      <div id="emptyHistoryHint" class="text-center text-[10px] text-[#7a8177] py-2 italic font-mono text-3d-header">
        [ 暂无古卷记录 · 按 = 刻入结果 ]
      </div>
      <div id="historyListContainer"></div>
    </div>
    
    <!-- 第三行：大号 3D 实体主结果输出 (空间充裕，绝无遮挡) -->
    <div class="main-display-stage pt-1 border-t border-[#a3a9a0]/60">
      <span id="pendingOpDisplay" class="text-sm font-mono text-[#575e54] pl-1 font-bold text-3d-header"></span>
      <span id="mainDisplay" class="text-3d-sculpt text-3xl tracking-wide max-w-full truncate pr-1">0</span>
    </div>
  </div>

  <!-- 按键网格 (大一倍字体，高度均匀贴合) -->
  <div class="grid grid-cols-4 gap-2.5">
    <button class="btn-3d-block btn-clay-fn" data-action="clear" data-note="220"><span class="btn-font-3d text-xl">AC</span></button>
    <button class="btn-3d-block btn-clay-fn" data-action="toggle-sign" data-note="246.9"><span class="btn-font-3d text-2xl">±</span></button>
    <button class="btn-3d-block btn-clay-fn" data-action="percent" data-note="293.7"><span class="btn-font-3d text-xl">%</span></button>
    <button class="btn-3d-block btn-clay-op" data-action="op" data-val="÷" data-note="392"><span class="btn-font-3d text-3xl">÷</span></button>

    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="7" data-note="329.6"><span class="btn-font-3d text-3xl">7</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="8" data-note="392"><span class="btn-font-3d text-3xl">8</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="9" data-note="440"><span class="btn-font-3d text-3xl">9</span></button>
    <button class="btn-3d-block btn-clay-op" data-action="op" data-val="×" data-note="329.6"><span class="btn-font-3d text-3xl">×</span></button>

    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="4" data-note="220"><span class="btn-font-3d text-3xl">4</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="5" data-note="246.9"><span class="btn-font-3d text-3xl">5</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="6" data-note="293.7"><span class="btn-font-3d text-3xl">6</span></button>
    <button class="btn-3d-block btn-clay-op" data-action="op" data-val="-" data-note="261.6"><span class="btn-font-3d text-3xl font-black">−</span></button>

    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="1" data-note="146.8"><span class="btn-font-3d text-3xl">1</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="2" data-note="164.8"><span class="btn-font-3d text-3xl">2</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="3" data-note="196"><span class="btn-font-3d text-3xl">3</span></button>
    <button class="btn-3d-block btn-clay-op" data-action="op" data-val="+" data-note="293.7"><span class="btn-font-3d text-3xl">＋</span></button>

    <button class="btn-3d-block btn-clay-num" data-action="num" data-val="0" data-note="110"><span class="btn-font-3d text-3xl">0</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="dot" data-note="261.6"><span class="btn-font-3d text-4xl leading-none">·</span></button>
    <button class="btn-3d-block btn-clay-num" data-action="delete" data-note="196"><span class="btn-font-3d text-2xl">⌫</span></button>
    <button class="btn-3d-block btn-clay-eq" data-action="calculate" data-note="146.8"><span class="btn-font-3d text-4xl">=</span></button>
  </div>

  <script>
    let soundEnabled = true;
    let audioCtx = null;

    function playGuqinTone(freq = 220, isChord = false) {
      if (!soundEnabled) return;
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;

        function pluckGuqinString(f, gainLevel = 0.32, duration = 1.2) {
          const osc1 = audioCtx.createOscillator();
          osc1.type = 'triangle';
          osc1.frequency.setValueAtTime(f, now);

          const osc2 = audioCtx.createOscillator();
          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(f * 2, now);

          const osc3 = audioCtx.createOscillator();
          osc3.type = 'sine';
          osc3.frequency.setValueAtTime(f * 3.01, now);

          const filter = audioCtx.createBiquadFilter();
          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(2400, now);
          filter.frequency.exponentialRampToValueAtTime(280, now + duration);

          const gainNode = audioCtx.createGain();
          gainNode.gain.setValueAtTime(0.0001, now);
          gainNode.gain.linearRampToValueAtTime(gainLevel, now + 0.005);
          gainNode.gain.exponentialRampToValueAtTime(gainLevel * 0.42, now + 0.09);
          gainNode.gain.exponentialRampToValueAtTime(0.0001, now + duration);

          osc1.connect(filter); osc2.connect(filter); osc3.connect(filter);
          filter.connect(gainNode); gainNode.connect(audioCtx.destination);
          osc1.start(now); osc2.start(now); osc3.start(now);
          osc1.stop(now + duration); osc2.stop(now + duration); osc3.stop(now + duration);
        }

        if (isChord) {
          pluckGuqinString(freq, 0.26, 1.4);
          setTimeout(() => pluckGuqinString(freq * 1.5, 0.22, 1.3), 32);
          setTimeout(() => pluckGuqinString(freq * 2, 0.18, 1.2), 64);
        } else {
          pluckGuqinString(freq);
        }
      } catch (e) {}
    }

    const soundToggle = document.getElementById('soundToggle');
    const soundIcon = document.getElementById('soundIcon');
    const soundLabel = document.getElementById('soundLabel');
    soundToggle.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      soundIcon.textContent = soundEnabled ? '🪕' : '🔇';
      soundLabel.textContent = soundEnabled ? '古琴开' : '静音';
    });

    let currentInput = '0';
    let previousInput = null;
    let activeOperator = null;
    let shouldResetInput = false;
    const historyList = [];

    const mainDisplay = document.getElementById('mainDisplay');
    const pendingOpDisplay = document.getElementById('pendingOpDisplay');
    const historyScrollBox = document.getElementById('historyScrollBox');
    const historyListContainer = document.getElementById('historyListContainer');
    const emptyHistoryHint = document.getElementById('emptyHistoryHint');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    function flashScreen() {
      mainDisplay.classList.remove('screen-hit');
      void mainDisplay.offsetWidth;
      mainDisplay.classList.add('screen-hit');
    }

    function updateDisplay() {
      const len = currentInput.length;
      mainDisplay.style.fontSize = len > 12 ? '1.25rem' : (len > 8 ? '1.55rem' : '2.0rem');
      mainDisplay.textContent = currentInput;
      pendingOpDisplay.textContent = (previousInput !== null && activeOperator !== null) ? `${previousInput} ${activeOperator}` : '';
    }

    function addHistoryRecord(expr, result) {
      historyList.push({ expr, result });
      emptyHistoryHint.style.display = 'none';

      const itemDiv = document.createElement('div');
      itemDiv.className = 'history-chip';
      itemDiv.title = '点击将此历史结果填入当前输入';
      itemDiv.innerHTML = `
        <span class="history-expr-3d truncate opacity-90"><span class="text-[#8c9489] mr-1">📐</span>${expr} =</span>
        <span class="history-val-3d ml-2 shrink-0">${result}</span>
      `;
      itemDiv.addEventListener('click', () => {
        currentInput = String(result);
        shouldResetInput = true;
        flashScreen();
        updateDisplay();
        playGuqinTone(293.7);
      });
      historyListContainer.appendChild(itemDiv);
      setTimeout(() => historyScrollBox.scrollTop = historyScrollBox.scrollHeight, 50);
    }

    clearHistoryBtn.addEventListener('click', () => {
      historyList.length = 0;
      historyListContainer.innerHTML = '';
      emptyHistoryHint.style.display = 'block';
      playGuqinTone(110);
    });

    function inputNumber(num) {
      currentInput = (shouldResetInput || currentInput === '0') ? num : (currentInput.length < 14 ? currentInput + num : currentInput);
      shouldResetInput = false;
      flashScreen(); updateDisplay();
    }

    function inputDot() {
      if (shouldResetInput) { currentInput = '0.'; shouldResetInput = false; }
      else if (!currentInput.includes('.')) currentInput += '.';
      flashScreen(); updateDisplay();
    }

    function handleOperator(op) {
      if (previousInput !== null && activeOperator && !shouldResetInput) computeResult(false);
      previousInput = currentInput; activeOperator = op; shouldResetInput = true;
      flashScreen(); updateDisplay();
    }

    function computeResult(isFinalEqual = true) {
      if (previousInput === null || activeOperator === null) return;
      const prev = parseFloat(previousInput); const curr = parseFloat(currentInput);
      let result = 0;
      switch (activeOperator) {
        case '+': result = prev + curr; break;
        case '-': result = prev - curr; break;
        case '×': result = prev * curr; break;
        case '÷':
          if (curr === 0) { currentInput = 'Error'; previousInput = null; activeOperator = null; shouldResetInput = true; flashScreen(); updateDisplay(); return; }
          result = prev / curr; break;
        default: return;
      }
      result = Math.round(result * 100000000) / 100000000;
      addHistoryRecord(`${previousInput} ${activeOperator} ${currentInput}`, result);
      currentInput = String(result);
      previousInput = isFinalEqual ? null : String(result);
      if (isFinalEqual) activeOperator = null;
      shouldResetInput = true; flashScreen(); updateDisplay();
    }

    function clearAll() { currentInput = '0'; previousInput = null; activeOperator = null; shouldResetInput = false; flashScreen(); updateDisplay(); }
    function toggleSign() { if (currentInput !== '0' && currentInput !== 'Error') { currentInput = currentInput.startsWith('-') ? currentInput.slice(1) : '-' + currentInput; flashScreen(); updateDisplay(); } }
    function handlePercent() { const val = parseFloat(currentInput); if (!isNaN(val)) { currentInput = String(val / 100); flashScreen(); updateDisplay(); } }
    function handleDelete() { if (shouldResetInput || currentInput === 'Error') clearAll(); else currentInput = currentInput.length > 1 ? currentInput.slice(0, -1) : '0'; flashScreen(); updateDisplay(); }

    document.querySelectorAll('.btn-3d-block').forEach(btn => {
      btn.addEventListener('pointerdown', (e) => {
        const action = btn.dataset.action;
        const val = btn.dataset.val;
        const noteFreq = parseFloat(btn.dataset.note) || 220;
        playGuqinTone(noteFreq, action === 'calculate');

        switch (action) {
          case 'num': inputNumber(val); break;
          case 'dot': inputDot(); break;
          case 'op': handleOperator(val); break;
          case 'calculate': computeResult(true); break;
          case 'clear': clearAll(); break;
          case 'toggle-sign': toggleSign(); break;
          case 'percent': handlePercent(); break;
          case 'delete': handleDelete(); break;
        }
      });
    });

    window.addEventListener('keydown', (e) => {
      const key = e.key;
      let sel = null;
      if (!isNaN(key)) sel = `[data-action="num"][data-val="${key}"]`;
      else if (key === '.') sel = '[data-action="dot"]';
      else if (key === '+' || key === '-') sel = `[data-action="op"][data-val="${key}"]`;
      else if (key === '*') sel = '[data-action="op"][data-val="×"]';
      else if (key === '/') { e.preventDefault(); sel = '[data-action="op"][data-val="÷"]'; }
      else if (key === 'Enter' || key === '=') { e.preventDefault(); sel = '[data-action="calculate"]'; }
      else if (key === 'Backspace') sel = '[data-action="delete"]';
      else if (key === 'Escape') sel = '[data-action="clear"]';
      if (sel) {
        const b = document.querySelector(sel);
        if (b) { b.classList.add('is-pressed'); b.dispatchEvent(new PointerEvent('pointerdown')); setTimeout(() => b.classList.remove('is-pressed'), 130); }
      }
    });

    updateDisplay();
  </script>
</body>
</html>
"""

def main():
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, "archi_3d_guqin_calc.html")
    profile_dir = os.path.join(temp_dir, "guqin_calc_profile")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CODE)

    file_uri = f"file:///{html_file.replace(os.sep, '/')}"

    # 设为屏幕大约 1/4 大小（标准紧凑桌面浮窗尺寸 380x620）
    target_w = 380
    target_h = 620

    # 1. 优先使用 pywebview
    try:
        import webview
        window = webview.create_window(
            '3D 雕塑石泥计算器 · 古琴音',
            html=HTML_CODE,
            width=target_w,
            height=target_h,
            resizable=True
        )
        webview.start()
        return
    except ImportError:
        pass

    # 2. Windows 原生独立小浮窗模式
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            pos_x = max(0, (sw - target_w) // 2)
            pos_y = max(0, (sh - target_h) // 2)
        except Exception:
            pos_x, pos_y = 120, 80

        # --user-data-dir 确保启动独立轻量实例，绝不继承主浏览器的全屏/最大化状态
        cmd = f'start msedge --app="{file_uri}" --user-data-dir="{profile_dir}" --window-size={target_w},{target_h} --window-position={pos_x},{pos_y}'
        try:
            subprocess.Popen(cmd, shell=True)

            # 后台守护检测：若窗口被意外最大化，自动还原为居中的 1/4 屏幕精致浮窗
            def monitor_window():
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    for _ in range(15):
                        time.sleep(0.15)
                        hwnd = user32.FindWindowW(None, '3D 雕塑石泥计算器 · 古琴音')
                        if hwnd:
                            # 9 = SW_RESTORE (取消最大化状态)
                            user32.ShowWindow(hwnd, 9)
                            # 0x0040 = SWP_SHOWWINDOW
                            user32.SetWindowPos(hwnd, 0, pos_x, pos_y, target_w, target_h, 0x0040)
                            break
                except Exception:
                    pass

            threading.Thread(target=monitor_window, daemon=True).start()
            return
        except Exception:
            pass

    # 3. 降级打开
    webbrowser.open(file_uri)

if __name__ == "__main__":
    main()