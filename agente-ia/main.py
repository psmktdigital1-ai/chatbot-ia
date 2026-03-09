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

# ─── AVATAR ──────────────────────────────────────────────────────────────────
AVATAR_B64 = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiMxZTJhM2EiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGQxNTIwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJib2R5LWdyYWQiIGN4PSI1MCUiIGN5PSIzMCUiIHI9IjcwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiICAgc3RvcC1jb2xvcj0iIzJhM2Y1ZiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTJhNDAiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImZhY2UtZ3JhZCIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiICAgc3RvcC1jb2xvcj0iIzFlM2E1YSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZjIwMzUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9InZpc29yLWdyYWQiIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgICBzdG9wLWNvbG9yPSIjNDBjNGZmIiBzdG9wLW9wYWNpdHk9IjAuNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDc3YWEiIHN0b3Atb3BhY2l0eT0iMC4yIi8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPGZpbHRlciBpZD0iZ2xvdyI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjIiIHJlc3VsdD0iYmx1ciIvPgogICAgICA8ZmVNZXJnZT48ZmVNZXJnZU5vZGUgaW49ImJsdXIiLz48ZmVNZXJnZU5vZGUgaW49IlNvdXJjZUdyYXBoaWMiLz48L2ZlTWVyZ2U+CiAgICA8L2ZpbHRlcj4KICAgIDxmaWx0ZXIgaWQ9InNvZnQtZ2xvdyI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjMiIHJlc3VsdD0iYmx1ciIvPgogICAgICA8ZmVNZXJnZT48ZmVNZXJnZU5vZGUgaW49ImJsdXIiLz48ZmVNZXJnZU5vZGUgaW49IlNvdXJjZUdyYXBoaWMiLz48L2ZlTWVyZ2U+CiAgICA8L2ZpbHRlcj4KICA8L2RlZnM+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSIxMDAiIGZpbGw9InVybCgjYmcpIi8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSI5NCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMWUzYTVhIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWRhc2hhcnJheT0iNiA0IiBvcGFjaXR5PSIwLjYiLz4KICA8cGF0aCBkPSJNMzAgMjAwIFEzMiAxNTUgNTIgMTQwIFE2OCAxMzIgMTAwIDEzNCBRMTMyIDEzMiAxNDggMTQwIFExNjggMTU1IDE3MCAyMDBaIiBmaWxsPSIjMGYxZjMwIi8+CiAgPHBhdGggZD0iTTgwIDEzNCBMMTAwIDE2MCBMODQgMjAwIEwzMCAyMDAgUTMyIDE2MCA1MiAxNDBaIiBmaWxsPSIjMTYyNTM1Ii8+CiAgPHBhdGggZD0iTTEyMCAxMzQgTDEwMCAxNjAgTDExNiAyMDAgTDE3MCAyMDAgUTE2OCAxNjAgMTQ4IDE0MFoiIGZpbGw9IiMxNjI1MzUiLz4KICA8cGF0aCBkPSJNOTUgMTM0IEwxMDAgMTQyIEwxMDUgMTM0IEwxMDIgMTY1IEwxMDAgMTcwIEw5OCAxNjVaIiBmaWxsPSIjMWE2YmFhIi8+CiAgPHBhdGggZD0iTTkzIDEzNCBMMTAwIDE0NSBMMTA3IDEzNCBMMTA1IDEzNCBMMTAwIDE0MiBMOTUgMTM0WiIgZmlsbD0iI2U4ZjBmOCIvPgogIDxyZWN0IHg9Ijg4IiB5PSIxMTgiIHdpZHRoPSIyNCIgaGVpZ2h0PSIxOCIgcng9IjYiIGZpbGw9IiMxYTJmNDUiLz4KICA8cmVjdCB4PSI0OCIgeT0iNDIiIHdpZHRoPSIxMDQiIGhlaWdodD0iODIiIHJ4PSIxOCIgZmlsbD0idXJsKCNmYWNlLWdyYWQpIiBzdHJva2U9IiMyYTRhNmEiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHJlY3QgeD0iNTQiIHk9IjQ4IiB3aWR0aD0iOTIiIGhlaWdodD0iNzAiIHJ4PSIxMyIgZmlsbD0iIzBmMWYzMCIgc3Ryb2tlPSIjMWUzYTU1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8cmVjdCB4PSIzNiIgeT0iNjIiIHdpZHRoPSIxNCIgaGVpZ2h0PSIzNiIgcng9IjUiIGZpbGw9IiMxNjI1MzUiIHN0cm9rZT0iIzJhNGE2NSIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPHJlY3QgeD0iMTUwIiB5PSI2MiIgd2lkdGg9IjE0IiBoZWlnaHQ9IjM2IiByeD0iNSIgZmlsbD0iIzE2MjUzNSIgc3Ryb2tlPSIjMmE0YTY1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8Y2lyY2xlIGN4PSI0MyIgY3k9Ijc4IiByPSI1IiBmaWxsPSIjMGYxZjJlIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxjaXJjbGUgY3g9IjQzIiBjeT0iNzgiIHI9IjIiIGZpbGw9IiMzOGJkZjgiIG9wYWNpdHk9IjAuOCIvPgogIDxjaXJjbGUgY3g9IjE1NyIgY3k9Ijc4IiByPSI1IiBmaWxsPSIjMGYxZjJlIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxjaXJjbGUgY3g9IjE1NyIgY3k9Ijc4IiByPSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjgiLz4KICA8cmVjdCB4PSI5NyIgeT0iMjgiIHdpZHRoPSI2IiBoZWlnaHQ9IjE4IiByeD0iMyIgZmlsbD0iIzFhM2E1NSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9IjI0IiByPSI3IiBmaWxsPSIjMGYxZjMwIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMjQiIHI9IjMuNSIgZmlsbD0iIzM4YmRmOCIgZmlsdGVyPSJ1cmwoI2dsb3cpIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswLjM7MSIgZHVyPSIyLjVzIiByZXBlYXRDb3VudD0iaW5kZWZpbml0ZSIvPgogIDwvY2lyY2xlPgogIDxyZWN0IHg9IjYwIiB5PSI2MiIgd2lkdGg9IjgwIiBoZWlnaHQ9IjI4IiByeD0iMTAiIGZpbGw9InVybCgjdmlzb3ItZ3JhZCkiIHN0cm9rZT0iIzM4YmRmOCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8ZWxsaXBzZSBjeD0iNzkiIGN5PSI3NiIgcng9IjEwIiByeT0iOCIgZmlsbD0iIzA1MTUyNSIgc3Ryb2tlPSIjMGVhNWU5IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8ZWxsaXBzZSBjeD0iNzkiIGN5PSI3NiIgcng9IjYiIHJ5PSI1IiBmaWxsPSIjMGVhNWU5IiBvcGFjaXR5PSIwLjkiIGZpbHRlcj0idXJsKCNnbG93KSIvPgogIDxlbGxpcHNlIGN4PSI3OSIgY3k9Ijc2IiByeD0iMyIgcnk9IjIuNSIgZmlsbD0iIzQwZTBmZiIvPgogIDxlbGxpcHNlIGN4PSIxMjEiIGN5PSI3NiIgcng9IjEwIiByeT0iOCIgZmlsbD0iIzA1MTUyNSIgc3Ryb2tlPSIjMGVhNWU5IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8ZWxsaXBzZSBjeD0iMTIxIiBjeT0iNzYiIHJ4PSI2IiByeT0iNSIgZmlsbD0iIzBlYTVlOSIgb3BhY2l0eT0iMC45IiBmaWx0ZXI9InVybCgjZ2xvdykiLz4KICA8ZWxsaXBzZSBjeD0iMTIxIiBjeT0iNzYiIHJ4PSIzIiByeT0iMi41IiBmaWxsPSIjNDBlMGZmIi8+CiAgPHJlY3QgeD0iNjgiIHk9Ijk4IiB3aWR0aD0iNjQiIGhlaWdodD0iMTgiIHJ4PSI2IiBmaWxsPSIjMGExODI1IiBzdHJva2U9IiMxZTNhNTUiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxyZWN0IHg9IjczIiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjg1IiBmaWx0ZXI9InVybCgjZ2xvdykiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjg1OzAuMzswLjg1IiBkdXI9IjEuOHMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0PgogIDxyZWN0IHg9Ijg1IiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjYiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjY7MTswLjYiIGR1cj0iMS4ycyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiLz4KICA8L3JlY3Q+CiAgPHJlY3QgeD0iOTciIHk9IjEwMyIgd2lkdGg9IjgiIGhlaWdodD0iOCIgcng9IjIiIGZpbGw9IiMzOGJkZjgiIG9wYWNpdHk9IjEiIGZpbHRlcj0idXJsKCNnbG93KSI+CiAgICA8YW5pbWF0ZSBhdHRyaWJ1dGVOYW1lPSJvcGFjaXR5IiB2YWx1ZXM9IjE7MC40OzEiIGR1cj0iMnMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0PgogIDxyZWN0IHg9IjEwOSIgeT0iMTAzIiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMiIgZmlsbD0iIzM4YmRmOCIgb3BhY2l0eT0iMC41Ij4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMC41OzAuOTswLjUiIGR1cj0iMS41cyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiLz4KICA8L3JlY3Q+CiAgPHJlY3QgeD0iMTIxIiB5PSIxMDMiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIyIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjc1IiBmaWx0ZXI9InVybCgjZ2xvdykiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIwLjc1OzAuMjswLjc1IiBkdXI9IjIuMnMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+CiAgPC9yZWN0Pgo8L3N2Zz4="

# ─── CSS ─────────────────────────────────────────────────────────────────────
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
.header {{ padding: 3.5rem 0 2rem; display: flex; flex-direction: column; align-items: center; }}
.avatar-circle {{
    width: 140px; height: 140px; border-radius: 50%; overflow: hidden;
    border: 2px solid #1e3a55; margin-bottom: 1.5rem;
    box-shadow: 0 0 0 4px rgba(56,189,248,0.08), 0 8px 36px rgba(0,0,0,0.65);
}}
.avatar-circle img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.header-name {{ font-family: 'Instrument Serif', serif; font-size: 3rem; font-weight: 400; color: #f0ede8; letter-spacing: -0.025em; line-height: 1; margin-bottom: 0.6rem; }}
.header-desc {{ font-size: 1.1rem; color: #b0a898; font-weight: 400; text-align: center; }}
.online {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 0.9rem; font-size: 0.9rem; color: #777; }}
.online-dot {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,0.5); }}
.sep {{ width: 36px; height: 1px; background: #2e2e2e; margin: 2rem auto 1.8rem; }}
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
.dash-metric {{ background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }}
.dash-metric-val {{ font-size: 2.5rem; font-weight: 700; color: #0ea5e9; font-family: 'Instrument Serif', serif; }}
.dash-metric-label {{ font-size: 0.85rem; color: #777; margin-top: 0.3rem; }}
.lead-card {{ background: #1a1a1a; border: 1px solid #252525; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }}
.lead-nicho {{ display: inline-block; background: #0ea5e920; color: #38bdf8; border-radius: 6px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600; }}
.lead-time {{ font-size: 0.78rem; color: #555; }}
</style>

<div class="header">
  <div class="avatar-circle"><img src="{AVATAR_B64}" alt="Paulo AI"/></div>
  <div class="header-name">Paulo AI</div>
  <div class="header-desc">Assistente com acesso à internet em tempo real</div>
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
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": mensagens,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
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
        sh     = gc.open_by_key(SHEET_ID)
        ws     = sh.sheet1
        if ws.row_count == 0 or ws.cell(1, 1).value != "Data/Hora":
            ws.insert_row(["Data/Hora","Sessão ID","Nicho Detectado","Cidade/Estado","Intenção","Primeira Pergunta","Total Mensagens"], 1)
        return ws
    except Exception:
        return None

def salvar_lead(dados: dict):
    ws = get_sheet()
    if not ws:
        return
    try:
        ws.append_row([
            dados.get("datetime", ""),
            dados.get("session_id", ""),
            dados.get("nicho", "Não identificado"),
            dados.get("cidade_estado", "Não informado"),
            dados.get("intencao", ""),
            dados.get("primeira_pergunta", ""),
            dados.get("total_msgs", 0),
        ])
    except Exception:
        pass

def carregar_leads():
    ws = get_sheet()
    if not ws:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

# ─── EXTRAÇÃO INTELIGENTE ─────────────────────────────────────────────────────
def extrair_dados_conversa(mensagens: list) -> dict:
    if not mensagens:
        return {}
    conversa_txt = "\n".join([f"{m['role'].upper()}: {m['content'][:300]}" for m in mensagens[:6]])
    prompt = f"""Analise essa conversa e extraia em JSON:
- nicho: setor do negócio do usuário (ex: Clínica/Saúde, Advocacia, Contabilidade, E-commerce, Restaurante, Outro)
- cidade_estado: cidade e estado mencionados (ex: São Paulo SP) ou "Não informado"
- intencao: o que o usuário quer em 1 linha curta

Conversa:
{conversa_txt}

Responda APENAS o JSON. Exemplo:
{{"nicho":"Clínica/Saúde","cidade_estado":"São Paulo SP","intencao":"Quer chatbot para clínica"}}"""
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
    with c1:
        st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{total}</div><div class="dash-metric-label">Total conversas</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{len(nichos)}</div><div class="dash-metric-label">Nichos</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{len(cidades)}</div><div class="dash-metric-label">Cidades</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="dash-metric"><div class="dash-metric-val" style="font-size:1.1rem">{nicho_top}</div><div class="dash-metric-label">Nicho top</div></div>', unsafe_allow_html=True)

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
        leads_f = [l for l in leads_f if t in str(l.get("Intenção","")).lower() or
                   t in str(l.get("Cidade/Estado","")).lower() or
                   t in str(l.get("Primeira Pergunta","")).lower()]

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
# CHAT
# ══════════════════════════════════════════════════════════════════════════════
for msg in st.session_state.lista_mensagens:
    st.chat_message(msg["role"]).write(msg["content"])

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
                 "oi", "olá", "ola", "tudo bem", "bom dia", "boa tarde", "boa noite"]
    return not any(p in pergunta.lower() for p in sem_busca)

mensagem_usuario = st.chat_input("Digite sua mensagem...")

if mensagem_usuario:
    if not st.session_state.lista_mensagens:
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
        f"Você é Paulo AI, assistente inteligente e conversacional com acesso à internet em tempo real.\n"
        f"REGRAS:\n"
        f"1. Se alguém disser 'oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'tudo bem' ou cumprimentos, responda de forma amigável e natural — NUNCA interprete como sigla.\n"
        f"2. Use [CONTEXTO DA INTERNET] como fonte principal quando disponível, citando as fontes.\n"
        f"3. Responda sempre em português brasileiro de forma clara e útil.\n"
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

    total_msgs = len(st.session_state.lista_mensagens)
    st.session_state.dados_lead["total_msgs"] = total_msgs

    if total_msgs >= 2 and not st.session_state.lead_salvo:
        dados_extraidos = extrair_dados_conversa(st.session_state.lista_mensagens)
        st.session_state.dados_lead.update(dados_extraidos)
        salvar_lead(st.session_state.dados_lead)
        st.session_state.lead_salvo = True
