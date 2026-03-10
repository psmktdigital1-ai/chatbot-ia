import streamlit as st
import requests
from tavily import TavilyClient
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import gspread
from google.oauth2.service_account import Credentials
import json
import re

st.set_page_config(page_title="Paulo AI", page_icon="✦", layout="centered")
st_autorefresh(interval=600000, limit=None, key="keepalive")

# ─── AVATAR ───────────────────────────────────────────────────────────────────
AVATAR_B64 = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiMxZTJhM2EiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGQxNTIwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJib2R5LWdyYWQiIGN4PSI1MCUiIGN5PSIzMCUiIHI9IjcwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiICAgc3RvcC1jb2xvcj0iIzJhM2Y1ZiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTJhNDAiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImZhY2UtZ3JhZCIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiICAgc3RvcC1jb2xvcj0iIzFlM2E1YSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZjIwMzUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9InZpc29yLWdyYWQiIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgICBzdG9wLWNvbG9yPSIjNDBjNGZmIiBzdG9wLW9wYWNpdHk9IjAuNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDc3YWEiIHN0b3Atb3BhY2l0eT0iMC4yIi8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPGZpbHRlciBpZD0iZ2xvdyI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjIiIHJlc3VsdD0iYmx1ciIvPgogICAgICA8ZmVNZXJnZT48ZmVNZXJnZU5vZGUgaW49ImJsdXIiLz48ZmVNZXJnZU5vZGUgaW49IlNvdXJjZUdyYXBoaWMiLz48L2ZlTWVyZ2U+CiAgICA8L2ZpbHRlcj4KICAgIDxmaWx0ZXIgaWQ9InNvZnQtZ2xvdyI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjMiIHJlc3VsdD0iYmx1ciIvPgogICAgICA8ZmVNZXJnZT48ZmVNZXJnZU5vZGUgaW49ImJsdXIiLz48ZmVNZXJnZU5vZGUgaW49IlNvdXJjZUdyYXBoaWMiLz48L2ZlTWVyZ2U+CiAgICA8L2ZpbHRlcj4KICA8L2RlZnM+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSIxMDAiIGZpbGw9InVybCgjYmcpIi8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSI5NCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMWUzYTVhIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWRhc2hhcnJheT0iNiA0IiBvcGFjaXR5PSIwLjYiLz4KICA8cGF0aCBkPSJNMzAgMjAwIFEzMiAxNTUgNTIgMTQwIFE2OCAxMzIgMTAwIDEzNCBRMTMyIDEzMiAxNDggMTQwIFExNjggMTU1IDE3MCAyMDBaIiBmaWxsPSIjMGYxZjMwIi8+CiAgPHBhdGggZD0iTTgwIDEzNCBMMTAwIDE2MCBMODQgMjAwIEwzMCAyMDAgUTMyIDE2MCA1MiAxNDBaIiBmaWxsPSIjMTYyNTM1Ii8+CiAgPHBhdGggZD0iTTEyMCAxMzQgTDEwMCAxNjAgTDExNiAyMDAgTDE3MCAyMDAgUTE2OCAxNjAgMTQ4IDE0MFoiIGZpbGw9IiMxNjI1MzUiLz4KICA8cGF0aCBkPSJNOTUgMTM0IEwxMDAgMTQyIEwxMDUgMTM0IEwxMDIgMTY1IEwxMDAgMTcwIEw5OCAxNjVaIiBmaWxsPSIjMWE2YmFhIi8+CiAgPHBhdGggZD0iTTkzIDEzNCBMMTAwIDE0NSBMMTA3IDEzNCBMMTA1IDEzNCBMMTAwIDE0MiBMOTUgMTM0WiIgZmlsbD0iI2U4ZjBmOCIvPgogIDxyZWN0IHg9Ijg4IiB5PSIxMTgiIHdpZHRoPSIyNCIgaGVpZ2h0PSIxOCIgcng9IjYiIGZpbGw9IiMxYTJmNDUiLz4KICA8cmVjdCB4PSI0OCIgeT0iNDIiIHdpZHRoPSIxMDQiIGhlaWdodD0iODIiIHJ4PSIxOCIgZmlsbD0idXJsKCNmYWNlLWdyYWQpIiBzdHJva2U9IiMyYTRhNmEiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHJlY3QgeD0iNTQiIHk9IjQ4IiB3aWR0aD0iOTIiIGhlaWdodD0iNzAiIHJ4PSIxMyIgZmlsbD0iIzBmMWYzMCIgc3Ryb2tlPSIjMWUzYTU1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8cmVjdCB4PSIzNiIgeT0iNjIiIHdpZHRoPSIxNCIgaGVpZ2h0PSIzNiIgcng9IjUiIGZpbGw9IiMxNjI1MzUiIHN0cm9rZT0iIzJhNGE2NSIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPHJlY3QgeD0iMTUwIiB5PSI2MiIgd2lkdGg9IjE0IiBoZWlnaHQ9IjM2IiByeD0iNSIgZmlsbD0iIzE2MjUzNSIgc3Ryb2tlPSIjMmE0YTY1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8Y2lyY2xlIGN4PSI0MyIgY3k9Ijc4IiByPSI1IiBmaWxsPSIjMGYxZjJlIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxjaXJjbGUgY3g9IjQzIiBjeT0iNzgiIHI9IjIiIGZpbGw9IiMzOGJkZjgiIG9wYWNpdHk9IjAuOCIvPgogIDxjaXJjbGUgY3g9IjE1NyIgY3k9Ijc4IiByPSI1IiBmaWxsPSIjMGYxZjJlIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxjaXJjbGUgY3g9IjE1NyIgY3k9Ijc4IiByPSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjgiLz4KICA8cmVjdCB4PSI5NyIgeT0iMjgiIHdpZHRoPSI2IiBoZWlnaHQ9IjE4IiByeD0iMyIgZmlsbD0iIzFhM2E1NSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9IjI0IiByPSI3IiBmaWxsPSIjMGYxZjMwIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMjQiIHI9IjMuNSIgZmlsbD0iIzM4YmRmOCIgZmlsdGVyPSJ1cmwoI2dsb3cpIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswLjM7MSIgZHVyPSIyLjVzIiByZXBlYXRDb3VudD0iaW5kZWZpbml0ZSIvPgogIDwvY2lyY2xlPgogIDxyZWN0IHg9IjYwIiB5PSI2MiIgd2lkdGg9IjgwIiBoZWlnaHQ9IjI4IiByeD0iMTAiIGZpbGw9InVybCgjdmlzb3ItZ3JhZCkiIHN0cm9rZT0iIzM4YmRmOCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8ZWxsaXBzZSBjeD0iNzkiIGN5PSI3NiIgcng9IjEwIiByeT0iOCIgZmlsbD0iIzA1MTUyNSIgc3Ryb2tlPSIjMGVhNWU5IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8ZWxsaXBzZSBjeD0iNzkiIGN5PSI3NiIgcng9IjYiIHJ5PSI1IiBmaWxsPSIjMGVhNWU5IiBvcGFjaXR5PSIwLjkiIGZpbHRlcj0idXJsKCNnbG93KSIvPgogIDxlbGxpcHNlIGN4PSI3OSIgY3k9Ijc2IiByeD0iMyIgcnk9IjIuNSIgZmlsbD0iIzQwZTBmZiIvPgogIDxlbGxpcHNlIGN4PSIxMjEiIGN5PSI3NiIgcng9IjEwIiByeT0iOCIgZmlsbD0iIzA1MTUyNSIgc3Ryb2tlPSIjMGVhNWU5IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8ZWxsaXBzZSBjeD0iMTIxIiBjeT0iNzYiIHJ4PSI2IiByeT0iNSIgZmlsbD0iIzBlYTVlOSIgb3BhY2l0eT0iMC45IiBmaWx0ZXI9InVybCgjZ2xvdykiLz4KICA8ZWxsaXBzZSBjeD0iMTIxIiBjeT0iNzYiIHJ4PSIzIiByeT0iMi41IiBmaWxsPSIjNDBlMGZmIi8+CiAgPHJlY3QgeD0iNjgiIHk9Ijk4IiB3aWR0aD0iNjQiIGhlaWdodD0iMTgiIHJ4PSI2IiBmaWxsPSIjMGExODI1IiBzdHJva2U9IiMxZTNhNTUiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxyZWN0IHg9IjczIiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjg1IiBmaWx0ZXI9InVybCgjZ2xvdykiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjg1OzAuMzswLjg1IiBkdXI9IjEuOHMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0PgogIDxyZWN0IHg9Ijg1IiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjYiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjY7MTswLjYiIGR1cj0iMS4ycyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiLz4KICA8L3JlY3Q+CiAgPHJlY3QgeD0iOTciIHk9IjEwMyIgd2lkdGg9IjgiIGhlaWdodD0iOCIgcng9IjIiIGZpbGw9IiMzOGJkZjgiIG9wYWNpdHk9IjEiIGZpbHRlcj0idXJsKCNnbG93KSI+CiAgICA8YW5pbWF0ZSBhdHRyaWJ1dGVOYW1lPSJvcGFjaXR5IiB2YWx1ZXM9IjE7MC40OzEiIGR1cj0iMnMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0PgogIDxyZWN0IHg9IjEwOSIgeT0iMTAzIiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMiIgZmlsbD0iIzM4YmRmOCIgb3BhY2l0eT0iMC41Ij4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMC41OzAuOTswLjUiIGR1cj0iMS41cyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiLz4KICA8L3JlY3Q+CiAgPHJlY3QgeD0iMTIxIiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjc1IiBmaWx0ZXI9InVybCgjZ2xvdykiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjc1OzAuMjswLjc1IiBkdXI9IjIuMnMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0Pgo8L3N2Zz4="

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [data-testid="stAppViewContainer"] {{
    background: #141414 !important;
    font-family: 'Inter', sans-serif;
    color: #f0ede8;
}}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
.block-container {{ padding: 0 1.5rem 5rem !important; max-width: 740px !important; }}

/* ─ HEADER ─ */
.header {{ padding: 3.5rem 0 2rem; display: flex; flex-direction: column; align-items: center; }}
.avatar-circle {{
    width: 140px; height: 140px; border-radius: 50%; overflow: hidden;
    border: 2px solid #1e3a55; margin-bottom: 1.5rem;
    box-shadow: 0 0 0 4px rgba(56,189,248,0.08), 0 8px 36px rgba(0,0,0,0.65);
}}
.avatar-circle img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.header-name {{ font-family: 'Instrument Serif', serif; font-size: 3rem; font-weight: 400; color: #f0ede8; letter-spacing: -0.025em; line-height: 1; margin-bottom: 0.5rem; }}
.header-desc {{ font-size: 1rem; color: #b0a898; font-weight: 400; text-align: center; max-width: 460px; line-height: 1.6; }}
.online {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 0.9rem; font-size: 0.9rem; color: #777; }}
.online-dot {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,0.5); animation: blink 2s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
.sep {{ width: 36px; height: 1px; background: #2e2e2e; margin: 1.8rem auto 1.5rem; }}

/* ─ BLOCO APRESENTAÇÃO ─ */
.apresentacao {{
    background: linear-gradient(135deg, #191e2b 0%, #141820 100%);
    border: 1px solid #252d3d;
    border-radius: 16px;
    padding: 1.4rem 1.7rem 1.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}}
.apresentacao::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #0369a1, #38bdf8, #0369a1);
}}
.apres-titulo {{
    font-family: 'Instrument Serif', serif;
    font-size: 1.2rem; color: #f0ede8; margin-bottom: 0.55rem;
}}
.apres-texto {{
    font-size: 0.92rem; color: #8a8580; line-height: 1.75;
}}
.apres-texto b {{ color: #c8c4be; }}
.tag-row {{ display: flex; flex-wrap: wrap; gap: 7px; margin-top: 1rem; }}
.tag {{
    background: #0ea5e912; border: 1px solid #0ea5e928;
    color: #38bdf8; border-radius: 20px;
    padding: 3px 11px; font-size: 0.78rem; font-weight: 500;
}}

/* ─ ABAS ─ */
[data-testid="stTabs"] {{ margin-bottom: 1.5rem; }}
[data-testid="stTabs"] [role="tablist"] {{
    background: #1a1a1a !important; border-radius: 10px !important;
    padding: 4px !important; border: 1px solid #252525 !important; gap: 2px !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important; border: none !important;
    border-radius: 7px !important; color: #555 !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    padding: 0.4rem 1rem !important; transition: all 0.2s !important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    background: #0ea5e9 !important; color: #fff !important;
}}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {{
    color: #aaa !important;
}}
[data-testid="stTabs"] [data-testid="stTabPanel"] {{
    background: #181818 !important; border: 1px solid #242424 !important;
    border-radius: 12px !important; padding: 1.4rem 1.5rem !important;
    margin-top: 4px;
}}

/* ─ CARDS DAS ABAS ─ */
.info-card {{
    background: #1e1e1e; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 1.05rem 1.25rem; margin-bottom: 0.75rem;
}}
.info-card-head {{
    font-weight: 600; color: #dedad5; font-size: 0.93rem;
    margin-bottom: 0.4rem;
}}
.info-card-body {{
    font-size: 0.87rem; color: #777; line-height: 1.7;
}}
.info-card-body b {{ color: #a8a49f; }}
.preco-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:0.7rem; }}
.preco-badge {{
    background: #0ea5e918; border: 1px solid #0ea5e935;
    color: #38bdf8; border-radius: 6px;
    padding: 3px 11px; font-size: 0.79rem; font-weight: 600;
}}
.destaque {{
    background: #0ea5e90a; border-left: 3px solid #0ea5e9;
    border-radius: 0 8px 8px 0; padding: 0.65rem 1rem;
    margin-top: 0.75rem; font-size: 0.86rem; color: #888; line-height: 1.65;
}}

/* ─ CHAT ─ */
[data-testid="stChatMessage"] {{ background: transparent !important; border: none !important; padding: 0.2rem 0 !important; }}
[data-testid="stChatMessageContent"] {{
    background: #1e1e1e !important; border: 1px solid #2a2a2a !important;
    border-radius: 14px !important; padding: 1rem 1.25rem !important;
    font-size: 1.05rem !important; line-height: 1.75 !important;
    color: #d4d0cb !important; box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}}
[data-testid="stChatInputContainer"] {{ background: #141414 !important; border-top: 1px solid #222 !important; padding: 1rem 1.5rem !important; }}
[data-testid="stChatInput"] {{ background: #1e1e1e !important; border: 1px solid #2e2e2e !important; border-radius: 12px !important; color: #f0ede8 !important; font-size: 1.05rem !important; }}
[data-testid="stChatInput"]::placeholder {{ color: #555 !important; }}
[data-testid="stChatInputSubmitButton"] button {{ background: #0ea5e9 !important; border-radius: 9px !important; border: none !important; }}
[data-testid="stChatInputSubmitButton"] button:hover {{ opacity: 0.8 !important; }}
[data-testid="stSpinner"] > div {{ color: #777 !important; font-size: 0.95rem !important; }}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-thumb {{ background: #333; border-radius: 999px; }}

/* ─ DASHBOARD ─ */
.dash-metric {{ background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }}
.dash-metric-val {{ font-size: 2.5rem; font-weight: 700; color: #0ea5e9; font-family: 'Instrument Serif', serif; }}
.dash-metric-label {{ font-size: 0.85rem; color: #777; margin-top: 0.3rem; }}
.lead-card {{ background: #1a1a1a; border: 1px solid #252525; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }}
.lead-card:hover {{ border-color: #0ea5e9; }}
.lead-nicho {{ display: inline-block; background: #0ea5e920; color: #38bdf8; border-radius: 6px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600; }}
.lead-time {{ font-size: 0.78rem; color: #555; }}
</style>

<div class="header">
  <div class="avatar-circle"><img src="{AVATAR_B64}" alt="Paulo AI"/></div>
  <div class="header-name">Paulo AI</div>
  <div class="header-desc">Especialista em Chatbots e Automações com Inteligência Artificial</div>
  <div class="online"><span class="online-dot"></span>disponível agora</div>
</div>
<div class="sep"></div>
""", unsafe_allow_html=True)

# ─── CREDENCIAIS ──────────────────────────────────────────────────────────────
GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
SHEET_ID       = st.secrets["SHEET_ID"]

tavily = TavilyClient(api_key=TAVILY_API_KEY)

# ─── CHAMADA GROQ via requests ────────────────────────────────────────────────
def chamar_groq(mensagens, temperature=0.5, max_tokens=1024):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": mensagens,
                  "temperature": temperature, "max_tokens": max_tokens},
            timeout=30
        )
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao chamar IA: {str(e)}"

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
@st.cache_resource
def get_sheet():
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc     = gspread.authorize(creds)
        ws     = gc.open_by_key(SHEET_ID).sheet1
        if ws.row_count == 0 or ws.cell(1, 1).value != "Data/Hora":
            ws.insert_row(["Data/Hora","Sessão ID","Nicho Detectado","Cidade/Estado","Intenção","Primeira Pergunta","Total Mensagens"], 1)
        return ws
    except Exception:
        return None

def salvar_lead(dados: dict):
    ws = get_sheet()
    if not ws: return
    try:
        ws.append_row([
            dados.get("datetime", ""), dados.get("session_id", ""),
            dados.get("nicho", "Não identificado"), dados.get("cidade_estado", "Não informado"),
            dados.get("intencao", ""), dados.get("primeira_pergunta", ""), dados.get("total_msgs", 0),
        ])
    except Exception:
        pass

def carregar_leads():
    ws = get_sheet()
    if not ws: return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

# ─── EXTRAÇÃO INTELIGENTE ─────────────────────────────────────────────────────
def extrair_dados_conversa(mensagens: list) -> dict:
    if not mensagens: return {}
    conversa_txt = "\n".join([f"{m['role'].upper()}: {m['content'][:300]}" for m in mensagens[:6]])
    prompt = f"""Analise essa conversa e extraia em JSON:
- nicho: setor do negócio (ex: Clínica/Saúde, Advocacia, Contabilidade, E-commerce, Restaurante, Outro)
- cidade_estado: cidade e estado mencionados ou "Não informado"
- intencao: o que o usuário quer em 1 linha curta

Conversa:
{conversa_txt}

Responda APENAS o JSON:
{{"nicho":"...","cidade_estado":"...","intencao":"..."}}"""
    try:
        raw = chamar_groq([{"role": "user", "content": prompt}], temperature=0, max_tokens=150)
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception:
        return {}

# ─── SESSION STATE ────────────────────────────────────────────────────────────
defaults = {
    "lista_mensagens": [],
    "historico_ia": [],
    "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
    "lead_salvo": False,
    "dados_lead": {},
    "admin_ok": False,
    "boas_vindas_ok": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── ROTEAMENTO ───────────────────────────────────────────────────────────────
is_admin = st.query_params.get("admin") == "1"

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD ADMIN
# ══════════════════════════════════════════════════════════════════════════════
if is_admin:
    st.markdown("## 🤖 Paulo AI — Painel Admin")
    if not st.session_state.admin_ok:
        senha = st.text_input("Senha de acesso:", type="password", placeholder="Digite a senha...")
        if st.button("Entrar"):
            if senha == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        st.stop()

    st.markdown("---")
    leads = carregar_leads()
    total     = len(leads)
    nichos    = [l.get("Nicho Detectado","") for l in leads if l.get("Nicho Detectado","") not in ("","Não identificado")]
    cidades   = [l.get("Cidade/Estado","") for l in leads if l.get("Cidade/Estado","") not in ("","Não informado")]
    nicho_top = max(set(nichos), key=nichos.count) if nichos else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{total}</div><div class="dash-metric-label">Total conversas</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{len(nichos)}</div><div class="dash-metric-label">Nichos</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{len(cidades)}</div><div class="dash-metric-label">Cidades</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dash-metric"><div class="dash-metric-val" style="font-size:1.1rem">{nicho_top}</div><div class="dash-metric-label">Nicho top</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        opcoes = ["Todos"] + sorted(set(l.get("Nicho Detectado","") for l in leads if l.get("Nicho Detectado","")))
        filtro_nicho = st.selectbox("Filtrar por nicho:", opcoes)
    with col_f2:
        filtro_busca = st.text_input("Buscar:", placeholder="Ex: chatbot, São Paulo...")

    leads_f = leads
    if filtro_nicho != "Todos":
        leads_f = [l for l in leads_f if l.get("Nicho Detectado","") == filtro_nicho]
    if filtro_busca:
        t = filtro_busca.lower()
        leads_f = [l for l in leads_f if t in str(l.get("Intenção","")).lower()
                   or t in str(l.get("Cidade/Estado","")).lower()
                   or t in str(l.get("Primeira Pergunta","")).lower()]

    st.markdown(f"**{len(leads_f)} conversa(s) encontrada(s)**")
    st.markdown("---")
    if not leads_f:
        st.info("Nenhuma conversa ainda.")
    else:
        for lead in reversed(leads_f):
            nicho    = lead.get("Nicho Detectado", "—")
            cidade   = lead.get("Cidade/Estado", "—")
            intencao = lead.get("Intenção", "—")
            dt       = lead.get("Data/Hora", "—")
            perg     = str(lead.get("Primeira Pergunta", ""))[:80]
            msgs     = lead.get("Total Mensagens", "—")
            st.markdown(f"""<div class="lead-card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span class="lead-nicho">{nicho}</span>
                <span class="lead-time">{dt} · {msgs} msgs</span>
              </div>
              <div style="color:#d4d0cb;font-size:0.95rem;margin-bottom:4px"><b>Intenção:</b> {intencao}</div>
              <div style="color:#888;font-size:0.88rem"><b>Cidade:</b> {cidade} · <b>Pergunta:</b> "{perg}..."</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Sair do painel"):
        st.session_state.admin_ok = False
        st.query_params.clear()
        st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

# ─── BLOCO DE APRESENTAÇÃO FIXO ───────────────────────────────────────────────
st.markdown("""
<div class="apresentacao">
  <div class="apres-titulo">👋 Olá! Sou o Paulo</div>
  <div class="apres-texto">
    Ajudo empresas a <b>crescerem com Inteligência Artificial</b> — criando chatbots personalizados
    e automações que economizam tempo, capturam leads e melhoram o atendimento ao cliente.<br><br>
    Explore as abas abaixo para conhecer meus serviços, ou converse diretamente com minha IA
    que tem <b>acesso à internet em tempo real</b> e pode responder qualquer dúvida. 🚀
  </div>
  <div class="tag-row">
    <span class="tag">🤖 Chatbots com IA</span>
    <span class="tag">⚙️ Automações</span>
    <span class="tag">📊 Captura de Leads</span>
    <span class="tag">🌐 Pesquisa em tempo real</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── ABAS ─────────────────────────────────────────────────────────────────────
aba_chat, aba_chatbots, aba_automacoes = st.tabs(["💬 Converse comigo", "🤖 Chatbots com IA", "⚙️ Automações"])

# ── ABA: CHATBOTS ──────────────────────────────────────────────────────────────
with aba_chatbots:
    st.markdown("""
<div class="info-card">
  <div class="info-card-head">🤖 O que é um Chatbot com IA?</div>
  <div class="info-card-body">
    Um chatbot com IA é um assistente virtual treinado com as informações do seu negócio.
    Ele atende seus clientes <b>24h por dia, 7 dias por semana</b> — respondendo dúvidas,
    agendando consultas, qualificando leads e enviando propostas de forma automática e humanizada.
  </div>
</div>

<div class="info-card">
  <div class="info-card-head">💡 Para quem é ideal?</div>
  <div class="info-card-body">
    • <b>Clínicas e consultórios</b> — agendamento, triagem e lembretes automáticos<br>
    • <b>Advogados e contadores</b> — triagem e qualificação de clientes<br>
    • <b>E-commerce e lojas</b> — suporte, rastreio de pedidos e vendas<br>
    • <b>Qualquer negócio</b> que receba mensagens no WhatsApp, Instagram ou site
  </div>
</div>

<div class="info-card">
  <div class="info-card-head">✅ O que está incluso?</div>
  <div class="info-card-body">
    Treinamento da IA com os dados do seu negócio · Integração ao WhatsApp · Painel de
    gestão de leads · Relatórios automáticos · Suporte técnico contínuo
  </div>
  <div class="preco-row">
    <span class="preco-badge">Setup: R$ 1.500 – R$ 4.000</span>
    <span class="preco-badge">Mensal: R$ 300 – R$ 600</span>
  </div>
  <div class="destaque">
    💬 Tem dúvidas sobre o chatbot certo para o seu negócio? Clique na aba <b>Converse comigo</b> e pergunte!
  </div>
</div>
""", unsafe_allow_html=True)

# ── ABA: AUTOMAÇÕES ────────────────────────────────────────────────────────────
with aba_automacoes:
    st.markdown("""
<div class="info-card">
  <div class="info-card-head">⚙️ O que são Automações com IA?</div>
  <div class="info-card-body">
    Automações conectam seus sistemas e eliminam tarefas manuais repetitivas.
    Com IA, elas ficam mais inteligentes: tomam decisões, analisam dados e executam
    fluxos complexos <b>sem nenhuma intervenção humana</b>.
  </div>
</div>

<div class="info-card">
  <div class="info-card-head">🔗 Exemplos de automações</div>
  <div class="info-card-body">
    • <b>Disparo automático</b> de mensagens para novos leads no WhatsApp<br>
    • <b>Integração</b> entre formulários, planilhas, CRM e e-mail<br>
    • <b>Relatórios gerados por IA</b> e enviados automaticamente<br>
    • <b>Qualificação de leads</b> com IA antes de chegar ao comercial<br>
    • <b>Notificações em tempo real</b> para sua equipe via Slack ou WhatsApp
  </div>
</div>

<div class="info-card">
  <div class="info-card-head">💰 Investimento</div>
  <div class="info-card-body">
    Projetos desenvolvidos sob medida para os processos e sistemas do seu negócio.
  </div>
  <div class="preco-row">
    <span class="preco-badge">Projeto: R$ 2.500 – R$ 8.000</span>
    <span class="preco-badge">Consultoria: R$ 800 – R$ 2.000</span>
  </div>
  <div class="destaque">
    ⚙️ Quer saber qual automação faz sentido para o seu negócio? <b>Pergunte na aba ao lado!</b>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ABA: CHAT ──────────────────────────────────────────────────────────────────
with aba_chat:

    # ── Mensagem de boas-vindas automática da IA (somente na primeira vez) ──
    if not st.session_state.boas_vindas_ok:
        boas_vindas = (
            "Olá! 👋 Bem-vindo ao Paulo AI!\n\n"
            "Sou o assistente virtual do **Paulo**, especialista em **Chatbots com IA** e **Automações Inteligentes**.\n\n"
            "Posso te ajudar com:\n"
            "• Dúvidas sobre chatbots e automações para o seu negócio\n"
            "• Informações sobre serviços e valores\n"
            "• Pesquisas atualizadas sobre tecnologia, IA e tendências\n"
            "• Análise do seu negócio e sugestões personalizadas\n\n"
            "Como posso te ajudar hoje? 🚀"
        )
        st.chat_message("assistant").write(boas_vindas)
        st.session_state.lista_mensagens.append({"role": "assistant", "content": boas_vindas})
        st.session_state.historico_ia.append({"role": "assistant", "content": boas_vindas})
        st.session_state.boas_vindas_ok = True
    else:
        for msg in st.session_state.lista_mensagens:
            st.chat_message(msg["role"]).write(msg["content"])

    # ── Funções de busca ──
    def buscar_internet(pergunta):
        try:
            resposta = tavily.search(query=pergunta, search_depth="advanced", max_results=5)
            resultados = ""
            for r in resposta["results"]:
                resultados += f"\nTítulo: {r['title']}\nConteúdo: {r['content']}\nFonte: {r['url']}\n"
            return resultados.strip()
        except Exception as e:
            return f"Erro ao buscar: {str(e)}"

    def precisa_buscar(pergunta):
        sem_busca = ["como se escreve", "o que significa", "defina", "qual a fórmula",
                     "me conta uma piada", "escreva um poema", "traduza", "corrija",
                     "oi", "olá", "ola", "tudo bem", "bom dia", "boa tarde", "boa noite",
                     "obrigado", "valeu", "ok", "entendi", "legal", "certo"]
        return not any(p in pergunta.lower() for p in sem_busca)

    # ── Input do chat ──
    mensagem_usuario = st.chat_input("Digite sua mensagem...")

    if mensagem_usuario:
        # Salva primeira pergunta real (ignora a boas-vindas)
        msgs_usuario = [m for m in st.session_state.lista_mensagens if m["role"] == "user"]
        if not msgs_usuario:
            st.session_state.dados_lead["primeira_pergunta"] = mensagem_usuario
            st.session_state.dados_lead["datetime"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.session_state.dados_lead["session_id"] = st.session_state.session_id

        st.chat_message("user").write(mensagem_usuario)
        st.session_state.lista_mensagens.append({"role": "user", "content": mensagem_usuario})

        contexto_busca = ""
        if precisa_buscar(mensagem_usuario):
            with st.spinner("Buscando informações atualizadas..."):
                resultado = buscar_internet(mensagem_usuario)
                if resultado:
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    contexto_busca = f"[CONTEXTO DA INTERNET - {data_hoje}]\nUse como fonte principal:\n{resultado}\n[FIM]"

        system_prompt = (
            f"Você é Paulo AI, assistente virtual do Paulo — especialista em Chatbots com IA e Automações Inteligentes.\n"
            f"SOBRE O PAULO:\n"
            f"- Especialista em chatbots personalizados com IA e automações de processos\n"
            f"- Atende clínicas, advogados, contadores, e-commerce e qualquer negócio\n"
            f"- Chatbot: R$1.500-4.000 setup + R$300-600/mês | Automações: R$2.500-8.000 | Consultoria: R$800-2.000\n"
            f"REGRAS:\n"
            f"1. Cumprimentos ('oi', 'olá', 'bom dia') — responda de forma amigável e natural, nunca interprete como sigla.\n"
            f"2. Use [CONTEXTO DA INTERNET] como fonte principal quando disponível, cite as fontes.\n"
            f"3. Quando falarem de chatbot ou automação, seja específico e mostre como o Paulo pode ajudar.\n"
            f"4. Responda sempre em português brasileiro de forma clara e profissional.\n"
            f"Hoje: {datetime.now().strftime('%d/%m/%Y')}"
        )

        conteudo_atual = f"{contexto_busca}\n\nPergunta: {mensagem_usuario}" if contexto_busca else mensagem_usuario
        st.session_state.historico_ia.append({"role": "user", "content": conteudo_atual})
        mensagens_ia = [{"role": "system", "content": system_prompt}] + st.session_state.historico_ia

        with st.spinner("Paulo AI está pensando..."):
            resposta_ia = chamar_groq(mensagens_ia)

        st.chat_message("assistant").write(resposta_ia)
        st.session_state.lista_mensagens.append({"role": "assistant", "content": resposta_ia})
        st.session_state.historico_ia.append({"role": "assistant", "content": resposta_ia})

        total_msgs = len([m for m in st.session_state.lista_mensagens if m["role"] == "user"])
        st.session_state.dados_lead["total_msgs"] = total_msgs

        if total_msgs >= 2 and not st.session_state.lead_salvo:
            dados_extraidos = extrair_dados_conversa(st.session_state.lista_mensagens)
            st.session_state.dados_lead.update(dados_extraidos)
            salvar_lead(st.session_state.dados_lead)
            st.session_state.lead_salvo = True
