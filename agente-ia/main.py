import streamlit as st
import google.generativeai as genai
import requests
from tavily import TavilyClient
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os, json, uuid, re
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Paulo AI", page_icon="✦", layout="centered", menu_items={"Get Help": None, "Report a bug": None, "About": None})
st_autorefresh(interval=600000, limit=None, key="keepalive")

AVATAR_B64 = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiMxZTJhM2EiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGQxNTIwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogIDwvZGVmcz4KICA8Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0idXJsKCNiZykiLz4KICA8cmVjdCB4PSI0OCIgeT0iNDIiIHdpZHRoPSIxMDQiIGhlaWdodD0iODIiIHJ4PSIxOCIgZmlsbD0iIzBmMWYzMCIgc3Ryb2tlPSIjMmE0YTZhIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDxyZWN0IHg9IjYwIiB5PSI2MiIgd2lkdGg9IjgwIiBoZWlnaHQ9IjI4IiByeD0iMTAiIGZpbGw9InJnYmEoNTYsODksMjQ4LDAuMTUpIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPGVsbGlwc2UgY3g9Ijc5IiBjeT0iNzYiIHJ4PSI4IiByeT0iNiIgZmlsbD0iIzBlYTVlOSIgb3BhY2l0eT0iMC45Ii8+CiAgPGVsbGlwc2UgY3g9IjEyMSIgY3k9Ijc2IiByeD0iOCIgcnk9IjYiIGZpbGw9IiMwZWE1ZTkiIG9wYWNpdHk9IjAuOSIvPgogIDxyZWN0IHg9IjY4IiB5PSI5OCIgd2lkdGg9IjY0IiBoZWlnaHQ9IjE2IiByeD0iNSIgZmlsbD0iIzBhMTgyNSIgc3Ryb2tlPSIjMWUzYTU1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8cmVjdCB4PSI5NyIgeT0iMTAzIiB3aWR0aD0iOCIgaGVpZ2h0PSI2IiByeD0iMiIgZmlsbD0iIzM4YmRmOCIvPgogIDxwYXRoIGQ9Ik0zMCAyMDAgUTMyIDE1NSA1MiAxNDAgUTY4IDEzMiAxMDAgMTM0IFExMzIgMTMyIDE0OCAxNDAgUTE2OCAxNTUgMTcwIDIwMFoiIGZpbGw9IiMwZjFmMzAiLz4KPC9zdmc+"

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[data-testid="stAppViewContainer"]{{background:#141414!important;font-family:'Inter',sans-serif;color:#ffffff}}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="manage-app-button"]{{display:none!important}}
#MainMenu{{display:none!important}}
footer{{display:none!important}}
[class*="viewerBadge"]{{display:none!important}}
[class*="StatusWidget"]{{display:none!important}}
[class*="stAppDeployButton"]{{display:none!important}}
[data-testid="stAppDeployButton"]{{display:none!important}}
div[class*="streamlit-wide"] div[class*="block-container"] + div{{display:none!important}}
ifr + div{{display:none!important}}
.st-emotion-cache-h5rgaw{{display:none!important}}
.st-emotion-cache-1dp5vir{{display:none!important}}
#stDecoration{{display:none!important}}
div[data-testid="collapsedControl"]{{display:none!important}}
footer, footer *{{visibility:hidden!important;display:none!important}}
.st-emotion-cache-164nlkn{{display:none!important}}
.st-emotion-cache-1dp5vir{{display:none!important}}
section[data-testid="stSidebar"] + div > div > div:last-child{{display:none!important}}
.block-container{{padding:0 1.5rem 5rem!important;max-width:740px!important}}
.header{{padding:3.5rem 0 2rem;display:flex;flex-direction:column;align-items:center}}
.avatar-circle{{width:120px;height:120px;border-radius:50%;overflow:hidden;border:2px solid #1e3a55;margin-bottom:1.2rem;box-shadow:0 0 0 4px rgba(56,189,248,0.08),0 8px 36px rgba(0,0,0,0.65)}}
.avatar-circle img{{width:100%;height:100%;object-fit:cover;display:block}}
.header-name{{font-family:'Instrument Serif',serif;font-size:2.8rem;font-weight:400;color:#ffffff;letter-spacing:-0.025em;line-height:1;margin-bottom:0.5rem}}
.header-desc{{font-size:1rem;color:#d0cdc8;text-align:center}}
.online{{display:inline-flex;align-items:center;gap:6px;margin-top:0.6rem;font-size:0.85rem;color:#aaa}}
.online-dot{{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px rgba(34,197,94,0.5);animation:blink 2s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
.nicho-badge{{display:inline-flex;align-items:center;gap:6px;margin-top:0.5rem;font-size:0.78rem;color:#38bdf8;background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);padding:4px 12px;border-radius:100px}}
.sep{{width:36px;height:1px;background:#2e2e2e;margin:1.8rem auto 1.5rem}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:0.2rem 0!important}}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li,[data-testid="stChatMessage"] span{{color:#ffffff!important}}
[data-testid="stChatMessage"] a{{color:#38bdf8!important}}
[data-testid="stChatInput"]{{background:#ffffff!important;border:1px solid #dddddd!important;border-radius:14px!important}}
[data-testid="stChatInput"] textarea{{color:#111111!important;font-size:1.05rem!important}}
[data-testid="stChatInput"] textarea::placeholder{{color:#888!important}}
[data-testid="stChatInputSubmitButton"] button{{background:#0ea5e9!important;border-radius:9px!important;border:none!important}}
::-webkit-scrollbar{{width:4px}}::-webkit-scrollbar-thumb{{background:#333;border-radius:999px}}
@media (max-width:768px){{[data-testid="stBottom"]{{display:block!important;visibility:visible!important;position:fixed!important;bottom:0!important;left:0!important;right:0!important;z-index:9998!important;background:#141414!important;padding:0.5rem 1rem 1rem!important;border-top:1px solid #2a2a2a!important}}.block-container{{padding-bottom:6rem!important}}}}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"]{{background:#1a1a1a!important;border-radius:10px!important;padding:4px!important;border:1px solid #252525!important}}
[data-testid="stTabs"] button[role="tab"]{{background:transparent!important;border:none!important;border-radius:7px!important;color:#555!important;font-size:0.85rem!important;font-weight:500!important;padding:0.4rem 0.9rem!important;transition:all 0.2s!important}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{{background:#0ea5e9!important;color:#fff!important}}
[data-testid="stTabs"] [data-testid="stTabPanel"]{{background:#181818!important;border:1px solid #242424!important;border-radius:12px!important;padding:1.4rem 1.5rem!important;margin-top:4px}}

/* ── DASHBOARD CARDS ── */
.metric-card{{background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:1.3rem 1.5rem;text-align:center;position:relative;overflow:hidden}}
.metric-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#0369a1,#38bdf8)}}
.metric-val{{font-family:'Instrument Serif',serif;font-size:2.4rem;font-weight:400;color:#38bdf8;line-height:1}}
.metric-label{{font-size:0.8rem;color:#666;margin-top:0.4rem;text-transform:uppercase;letter-spacing:0.06em}}
.lead-card{{background:#1a1a1a;border:1px solid #252525;border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;transition:border-color 0.2s}}
.lead-card:hover{{border-color:#0ea5e960}}
.lead-card.quente{{border-left:3px solid #ef4444}}
.lead-card.morno{{border-left:3px solid #f59e0b}}
.lead-card.frio{{border-left:3px solid #6b7280}}
.badge{{display:inline-block;border-radius:6px;padding:2px 9px;font-size:0.75rem;font-weight:600}}
.badge-nicho{{background:#0ea5e915;color:#38bdf8;border:1px solid #0ea5e930}}
.badge-quente{{background:#ef444415;color:#ef4444;border:1px solid #ef444430}}
.badge-morno{{background:#f59e0b15;color:#f59e0b;border:1px solid #f59e0b30}}
.badge-frio{{background:#6b728015;color:#9ca3af;border:1px solid #6b728030}}
.badge-score{{background:#7c3aed15;color:#a78bfa;border:1px solid #7c3aed30}}
.chart-bar-wrap{{margin:0.3rem 0}}
.chart-label{{font-size:0.8rem;color:#888;margin-bottom:3px}}
.chart-bar-bg{{background:#242424;border-radius:4px;height:8px;overflow:hidden}}
.chart-bar-fill{{height:8px;border-radius:4px;background:linear-gradient(90deg,#0369a1,#38bdf8)}}
.section-title{{font-family:'Instrument Serif',serif;font-size:1.3rem;color:#f0ede8;margin-bottom:1rem}}
</style>

<div class="header">
  <div class="avatar-circle"><img src="{AVATAR_B64}" alt="Paulo AI"/></div>
  <div class="header-name">Paulo AI</div>
  <div class="header-desc">Assistente inteligente com acesso à internet em tempo real</div>
  <div class="online"><span class="online-dot"></span> disponível agora</div>
</div>
<div class="sep"></div>
""", unsafe_allow_html=True)

# ── BOTÃO FLUTUANTE WHATSAPP ──────────────────────────────────
st.markdown("""
<style>
.whatsapp-float{position:fixed;bottom:28px;right:28px;z-index:9999;display:flex;align-items:center;gap:10px;text-decoration:none;animation:fadeInUp 0.6s ease}
@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.whatsapp-bubble{background:#25d366;border-radius:50%;width:58px;height:58px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px rgba(37,211,102,0.45);transition:transform 0.2s,box-shadow 0.2s}
.whatsapp-bubble:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(37,211,102,0.6)}
.whatsapp-bubble svg{width:30px;height:30px;fill:#fff}
.whatsapp-label{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:6px 12px;font-size:0.8rem;color:#d4d0cb;white-space:nowrap;box-shadow:0 2px 12px rgba(0,0,0,0.4);opacity:0;transform:translateX(10px);transition:opacity 0.2s,transform 0.2s;pointer-events:none}
.whatsapp-float:hover .whatsapp-label{opacity:1;transform:translateX(0)}
</style>
<a class="whatsapp-float" href="https://wa.me/5511951131232?text=Ol%C3%A1%20Paulo%2C%20vi%20seu%20assistente%20de%20IA%20e%20quero%20saber%20mais!" target="_blank">
  <span class="whatsapp-label">Falar com o Paulo</span>
  <div class="whatsapp-bubble">
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 2C8.28 2 2 8.28 2 16c0 2.47.67 4.78 1.84 6.76L2 30l7.45-1.81A13.93 13.93 0 0016 30c7.72 0 14-6.28 14-14S23.72 2 16 2zm7.37 19.63c-.31.87-1.53 1.59-2.52 1.8-.67.14-1.55.25-4.5-1.02-3.78-1.6-6.22-5.43-6.41-5.68-.18-.25-1.5-2-.1-3.8a2.3 2.3 0 011.7-.9c.21 0 .4.01.57.02.5.02.75.05 1.08.84.4 1 1.37 3.44 1.49 3.69.12.25.2.54.04.87-.15.34-.27.5-.52.78-.25.28-.49.5-.74.8-.22.27-.47.56-.19 1.06.28.5 1.24 2.04 2.65 3.3 1.82 1.62 3.33 2.13 3.88 2.36.54.23.86.19 1.18-.12.32-.31 1.23-1.44 1.56-1.93.32-.5.65-.41 1.09-.25.44.16 2.8 1.32 3.28 1.56.48.24.8.36.92.56.12.2.12 1.07-.19 1.96z"/>
    </svg>
  </div>
</a>
""", unsafe_allow_html=True)

# ── ESCONDE BADGE STREAMLIT VIA JS ───────────────────────────
st.markdown("""
<script>
(function hideBadge(){
  var sel = [
    '[data-testid="stStatusWidget"]',
    '[data-testid="manage-app-button"]',
    '.st-emotion-cache-h5rgaw',
    '.st-emotion-cache-1dp5vir',
    'iframe[title*="streamlit"]'
  ];
  function remove(){
    sel.forEach(function(s){
      var el = document.querySelector(s);
      if(el) el.style.display='none';
    });
    // Remove "Hosted with Streamlit" bar at bottom
    var all = document.querySelectorAll('*');
    all.forEach(function(el){
      if(el.innerText && el.innerText.trim()==='Hosted with Streamlit'){
        el.parentElement.style.display='none';
      }
    });
  }
  remove();
  setInterval(remove, 500);
})();
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# API KEYS
# ══════════════════════════════════════════════════════════════
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY",   os.getenv("GROQ_API_KEY",   ""))
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY",  os.getenv("TAVILY_API_KEY", ""))
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD",  os.getenv("ADMIN_PASSWORD", "paulo2025"))
SHEET_ID       = st.secrets.get("SHEET_ID",        os.getenv("SHEET_ID", ""))
GOOGLE_CREDS   = st.secrets.get("GOOGLE_CREDS", st.secrets.get("GOOGLE_CREDENTIALS", os.getenv("GOOGLE_CREDS", "")))

if not TAVILY_API_KEY:
    st.error("⚠️ Configure TAVILY_API_KEY em .streamlit/secrets.toml")
    st.stop()
if not GEMINI_API_KEY and not GROQ_API_KEY:
    st.error("⚠️ Configure ao menos GEMINI_API_KEY ou GROQ_API_KEY em .streamlit/secrets.toml")
    st.stop()

# ══════════════════════════════════════════════════════════════
# GOOGLE SHEETS
# ══════════════════════════════════════════════════════════════
def get_sheet():
    try:
        if not GOOGLE_CREDS:
            st.sidebar.error("❌ GOOGLE_CREDS não configurado")
            return None
        if not SHEET_ID:
            st.sidebar.error("❌ SHEET_ID não configurado")
            return None
        creds_dict = json.loads(GOOGLE_CREDS)
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        try:
            ws = sh.worksheet("Leads")
        except Exception:
            ws = sh.add_worksheet("Leads", rows=2000, cols=12)
        cabecalho = ["Data/Hora","Sessão","Nome","Nicho","Cidade/Estado","Intenção","Score","Estágio","Primeira Pergunta","Total Msgs","Tempo na Sessão (min)"]
        primeira_linha = ws.row_values(1) if ws.row_count > 0 else []
        if primeira_linha != cabecalho:
            ws.clear()
            ws.insert_row(cabecalho, 1)
        return ws
    except Exception as e:
        st.sidebar.error(f"❌ Sheets erro: {e}")
        return None

def salvar_lead(dados: dict):
    ws = get_sheet()
    if not ws:
        st.sidebar.error("❌ Não conectou ao Sheets")
        return
    try:
        ws.append_row([
            dados.get("datetime", ""),
            dados.get("session_id", ""),
            dados.get("nome", ""),
            dados.get("nicho", ""),
            dados.get("cidade_estado", "Não informado"),
            dados.get("intencao", ""),
            dados.get("score", ""),
            dados.get("estagio", ""),
            dados.get("primeira_pergunta", "")[:300],
            dados.get("total_msgs", 0),
            dados.get("tempo_min", 0),
        ])
    except Exception as e:
        pass

def carregar_leads():
    ws = get_sheet()
    if not ws:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════
# IA: ANÁLISE DE LEAD (score + estágio + cidade + intenção)
# ══════════════════════════════════════════════════════════════
def analisar_lead_com_ia(nicho, mensagens):
    """Usa IA para extrair dados do lead e atribuir score e estágio."""
    if not mensagens:
        return {}
    conversa = "\n".join([f"{m['role'].upper()}: {m['content'][:300]}" for m in mensagens[:10]])
    prompt = f"""Analise essa conversa de um chatbot de vendas e retorne APENAS um JSON com:
- cidade_estado: cidade e estado mencionados (ex: "São Paulo SP") ou "Não informado"
- intencao: o que o lead quer em 1 frase curta (ex: "Quer chatbot para clínica")
- score: número de 1 a 10 indicando interesse em contratar (1=só curiosidade, 10=quer fechar agora)
- estagio: um de ["🥶 Frio","🌡️ Morno","🔥 Quente"] baseado no score (1-4=Frio, 5-7=Morno, 8-10=Quente)
- resumo: resumo da conversa em 1 linha

Nicho: {nicho}
Conversa:
{conversa}

Responda SOMENTE o JSON, sem explicação:
{{"cidade_estado":"...","intencao":"...","score":7,"estagio":"🌡️ Morno","resumo":"..."}}"""

    # tenta Gemini
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
            raw = model.generate_content(prompt).text
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception:
            pass
    # fallback Groq
    if GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0, "max_tokens": 200},
                timeout=20
            )
            raw = resp.json()["choices"][0]["message"]["content"]
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception:
            pass
    return {}

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "session_inicio" not in st.session_state:
    st.session_state.session_inicio = datetime.now()
if "msgs" not in st.session_state:
    st.session_state.msgs = {}
if "hist_gemini" not in st.session_state:
    st.session_state.hist_gemini = {}
if "lead_salvo" not in st.session_state:
    st.session_state.lead_salvo = False
if "dados_lead" not in st.session_state:
    st.session_state.dados_lead = {}
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""
if "nome_confirmado" not in st.session_state:
    st.session_state.nome_confirmado = False

# ══════════════════════════════════════════════════════════════
# NICHOS
# ══════════════════════════════════════════════════════════════
NICHOS = {
    "🏥 Clínica / Saúde": {
        "badge": "Especialista em Clínicas",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.
Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API

Serviços: Automação de Agendamento, Chatbot com IA, Dashboard de Performance, CRM, Lead Scoring, Relatórios Automáticos.

REGRAS:
1. No PRIMEIRO contato, apresente Paulo de forma calorosa e resumida. Finalize com: "Qual é a sua maior dor hoje? 😊"
2. Seja consultivo, prático e humano. Ao identificar uma dor, sugira como Paulo resolve.
3. Ao final de respostas relevantes, inclua CTA natural:
   4. Responda sempre em português brasileiro.

NICHO: Clínicas, consultórios e espaços de saúde.
EXPERTISE: agendamento automático, lembretes WhatsApp, redução de faltas, pós-consulta automático."""
    },
    "🏢 Corretora de Seguros": {
        "badge": "Especialista em Seguros",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação. Pós-graduado em Ciências de Dados & IA, trabalhou com corretoras aplicando automação com n8n, Python, GPT-4 e WhatsApp API.

Serviços: CRM + Cotação Automática, Chatbot com IA, Dashboard de Vendas, Lead Scoring, Follow-up Automático.

REGRAS:
1. No PRIMEIRO contato, apresente Paulo de forma calorosa. Finalize com: "Qual é a sua maior dor hoje? 😊"
2. Seja consultivo. Ao identificar dor operacional, mostre como Paulo resolve.
3. CTA: 4. Responda em português brasileiro.

NICHO: Corretoras de seguros.
EXPERTISE: cotação automática via WhatsApp, CRM de leads, follow-up de renovações, pipeline de vendas."""
    },
    "📊 Escritório Contábil": {
        "badge": "Especialista em Contabilidade",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação. Pós-graduado em Ciências de Dados & IA, trabalhou com escritórios contábeis automatizando cobranças, documentos e relatórios.

Serviços: Automação de Cobranças, Relatórios Automáticos, Chatbot de Atendimento, Dashboard de KPIs.

REGRAS:
1. No PRIMEIRO contato, apresente Paulo de forma calorosa. Finalize com: "Qual é a sua maior dor hoje? 😊"
2. Seja consultivo. Ao identificar dor, mostre como Paulo resolve.
3. CTA: 4. Responda em português brasileiro.

NICHO: Escritórios de contabilidade.
EXPERTISE: cobrança automática de documentos, DRE automático, lembretes de prazos fiscais."""
    },
    "✂️ Barbearia / Estética": {
        "badge": "Especialista em Barbearias",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação. Trabalhou com barbearias e salões criando sistemas de agendamento automático e retenção de clientes.

Serviços: Automação de Agendamento, Chatbot WhatsApp, Dashboard de Faturamento, Programa de Fidelidade.

REGRAS:
1. No PRIMEIRO contato, apresente Paulo de forma calorosa. Finalize com: "Qual é a sua maior dor hoje? 😊"
2. Seja consultivo. Ao identificar dor, mostre como Paulo resolve.
3. CTA: 4. Responda em português brasileiro.

NICHO: Barbearias, salões e estúdios de estética.
EXPERTISE: agendamento automático, redução de no-show, reativação de clientes inativos."""
    },
    "🛒 E-commerce / Loja": {
        "badge": "Especialista em E-commerce",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação. Trabalhou com e-commerces em Retail Media, automação de campanhas e dashboards de performance.

Serviços: Estratégia de Retail Media, Dashboard de Performance, Consultoria E-commerce, Chatbot de Suporte.

REGRAS:
1. No PRIMEIRO contato, apresente Paulo de forma calorosa. Finalize com: "Qual é a sua maior dor hoje? 😊"
2. Seja consultivo. Ao identificar dor, mostre como Paulo resolve.
3. CTA: 4. Responda em português brasileiro.

NICHO: E-commerce e lojas virtuais.
EXPERTISE: Amazon Ads, ML Ads, Shopee, análise de SKU e ROAS, automação de campanhas."""
    },
    "🤖 Geral": {
        "badge": "Chat Geral",
        "prompt": """Você é Paulo AI, assistente inteligente geral com acesso à internet em tempo real.
Responda qualquer pergunta: tecnologia, negócios, IA, automação, ciência, curiosidades e mais.
Seja útil, claro e direto. Responda em português brasileiro.
Quando relevante, mencione que Paulo Santos pode ajudar com automação e IA para negócios."""
    },
}

# ══════════════════════════════════════════════════════════════
# ROTEAMENTO: ADMIN ou CHAT
# ══════════════════════════════════════════════════════════════
is_admin = st.query_params.get("admin") == "1"

# ══════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD ADMIN
# ══════════════════════════════════════════════════════════════
if is_admin:
    st.markdown("## 🤖 Paulo AI — Painel de Leads")

    if not st.session_state.admin_ok:
        senha = st.text_input("Senha:", type="password", placeholder="Digite a senha de acesso...")
        if st.button("Entrar", type="primary"):
            if senha == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        st.stop()

    # ── Carrega leads ──
    leads = carregar_leads()
    total = len(leads)

    # ── Cálculos ──
    nichos_lista   = [l.get("Nicho","") for l in leads if l.get("Nicho","")]
    quentes        = [l for l in leads if "Quente" in str(l.get("Estágio",""))]
    mornos         = [l for l in leads if "Morno"  in str(l.get("Estágio",""))]
    scores         = [int(l["Score"]) for l in leads if str(l.get("Score","")).isdigit()]
    score_medio    = round(sum(scores)/len(scores), 1) if scores else 0

    # contagem por nicho
    nicho_count = {}
    for n in nichos_lista:
        nicho_count[n] = nicho_count.get(n, 0) + 1
    nicho_top = max(nicho_count, key=nicho_count.get) if nicho_count else "—"

    # ── Métricas ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total}</div><div class="metric-label">Total Leads</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#ef4444">{len(quentes)}</div><div class="metric-label">🔥 Leads Quentes</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#a78bfa">{score_medio}</div><div class="metric-label">Score Médio</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-val" style="font-size:1rem;padding-top:0.5rem">{nicho_top.split(" ")[-1] if nicho_top != "—" else "—"}</div><div class="metric-label">Nicho Top</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico por nicho ──
    if nicho_count:
        st.markdown('<div class="section-title">📊 Conversas por nicho</div>', unsafe_allow_html=True)
        max_val = max(nicho_count.values())
        for nicho_nome, count in sorted(nicho_count.items(), key=lambda x: -x[1]):
            pct = int((count / max_val) * 100)
            st.markdown(f"""
<div class="chart-bar-wrap">
  <div class="chart-label">{nicho_nome} <span style="color:#38bdf8;font-weight:600">{count}</span></div>
  <div class="chart-bar-bg"><div class="chart-bar-fill" style="width:{pct}%"></div></div>
</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Filtros ──
    st.markdown('<div class="section-title">🎯 Lista de Leads</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        opcoes_nicho = ["Todos"] + sorted(set(nichos_lista))
        filtro_nicho = st.selectbox("Nicho:", opcoes_nicho)
    with col2:
        filtro_estagio = st.selectbox("Estágio:", ["Todos","🔥 Quente","🌡️ Morno","🥶 Frio"])
    with col3:
        filtro_busca = st.text_input("Buscar:", placeholder="Palavra-chave...")

    leads_f = leads
    if filtro_nicho != "Todos":
        leads_f = [l for l in leads_f if l.get("Nicho","") == filtro_nicho]
    if filtro_estagio != "Todos":
        leads_f = [l for l in leads_f if filtro_estagio.split(" ")[-1] in str(l.get("Estágio",""))]
    if filtro_busca:
        t = filtro_busca.lower()
        leads_f = [l for l in leads_f if
                   t in str(l.get("Intenção","")).lower() or
                   t in str(l.get("Cidade/Estado","")).lower() or
                   t in str(l.get("Primeira Pergunta","")).lower()]

    st.markdown(f"**{len(leads_f)} lead(s) encontrado(s)**")
    st.markdown("<br>", unsafe_allow_html=True)

    if not leads_f:
        st.info("Nenhum lead ainda. As conversas aparecerão aqui automaticamente.")
    else:
        for lead in reversed(leads_f):
            nicho_l   = lead.get("Nicho", "—")
            nome_l    = lead.get("Nome", "")
            cidade    = lead.get("Cidade/Estado", "—")
            intencao  = lead.get("Intenção", "—")
            score     = lead.get("Score", "—")
            estagio   = lead.get("Estágio", "—")
            dt        = lead.get("Data/Hora", "—")
            perg      = str(lead.get("Primeira Pergunta", ""))[:90]
            msgs_n    = lead.get("Total Msgs", "—")
            tempo     = lead.get("Tempo na Sessão (min)", "—")

            # cor do card por estágio
            cor_card = "quente" if "Quente" in str(estagio) else ("morno" if "Morno" in str(estagio) else "frio")
            cor_badge = f"badge-{cor_card}"

            st.markdown(f"""
<div class="lead-card {cor_card}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;flex-wrap:wrap;gap:6px">
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      <span class="badge badge-nicho">{nicho_l}</span>
      <span class="badge {cor_badge}">{estagio}</span>
      <span class="badge badge-score">⭐ {score}/10</span>
    </div>
    <span style="font-size:0.75rem;color:#555">{dt} · {msgs_n} msgs · {tempo}min</span>
  </div>
  <div style="color:#d4d0cb;font-size:0.9rem;margin-bottom:4px">{"👤 <b>" + nome_l + "</b> · " if nome_l else ""}<b>Intenção:</b> {intencao}</div>
  <div style="color:#888;font-size:0.82rem"><b>📍 {cidade}</b> · "{perg}..."</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    if st.button("🚪 Sair do painel"):
        st.session_state.admin_ok = False
        st.query_params.clear()
        st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════
# PÁGINA: CHAT PRINCIPAL
# ══════════════════════════════════════════════════════════════

# ── CARD UNIFICADO: BOAS-VINDAS + NOME + NICHO ───────────────
st.markdown("""
<style>
.bv-card{background:#191e2b;border:1px solid #252d3d;border-radius:16px;padding:1.5rem 1.7rem 1.6rem;margin-bottom:1.4rem;position:relative;overflow:hidden}
.bv-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#0369a1,#38bdf8,#0369a1)}
.bv-titulo{font-size:1rem;font-weight:600;color:#f0ede8;margin-bottom:0.7rem}
.bv-item{display:flex;align-items:flex-start;gap:10px;margin-bottom:0.35rem;font-size:0.87rem;color:#777;line-height:1.5}
.bv-item b{color:#a8a49f}
.bv-divider{height:1px;background:#252d3d;margin:1rem 0}
.bv-nome-label{font-size:0.85rem;color:#888;margin-bottom:0.4rem;font-weight:500}
</style>
<div class="bv-card">
  <div class="bv-titulo">👋 Bem-vindo ao Paulo AI — veja o que você pode fazer aqui:</div>
  <div class="bv-item">💬 <span><b>Converse naturalmente</b> sobre o seu negócio, dores e desafios</span></div>
  <div class="bv-item">🔍 <span><b>Tire dúvidas</b> sobre automação, chatbots e IA com acesso à internet em tempo real</span></div>
  <div class="bv-item">🎯 <span><b>Selecione seu segmento</b> abaixo para uma conversa especializada no seu nicho</span></div>
  <div class="bv-item">📸 <span><b>Quer avançar?</b> Siga o Paulo no Instagram: <b>@paulosantos.growthai</b></span></div>
  <div class="bv-divider"></div>
  <div class="bv-nome-label">Como posso te chamar?</div>
</div>
""", unsafe_allow_html=True)

# Campo de nome — salva automaticamente ao digitar
nome_input = st.text_input("nome", placeholder="Ex: João Silva...",
                            label_visibility="collapsed", key="input_nome",
                            value=st.session_state.nome_usuario)
if nome_input.strip():
    st.session_state.nome_usuario = nome_input.strip()
    st.session_state.nome_confirmado = True
    if "saudacao_feita" not in st.session_state:
        st.session_state.saudacao_feita = False

st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

# ── SELETOR DE NICHO ──────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:1.2rem;padding:0 0.5rem">
  <div style="font-size:1.05rem;color:#ffffff;font-weight:600;margin-bottom:0.4rem">Qual é o seu segmento?</div>
  <div style="font-size:0.88rem;color:#b0b0b0;line-height:1.6">
    Selecione o nicho do seu negócio para uma conversa especializada —
    ou escolha <strong style="color:#b0a898">🤖 Geral</strong> para dúvidas livres sobre automação, dados e IA.
  </div>
</div>
""", unsafe_allow_html=True)

nicho = st.selectbox("Área:", list(NICHOS.keys()), label_visibility="collapsed")
config = NICHOS[nicho]
st.markdown(f'<div style="text-align:center;margin-bottom:1rem"><span class="nicho-badge">✦ {config["badge"]}</span></div>', unsafe_allow_html=True)

# ── ESTADO POR NICHO ──────────────────────────────────────────
for key in ["msgs", "hist_gemini"]:
    if nicho not in st.session_state[key]:
        st.session_state[key][nicho] = []

msgs     = st.session_state.msgs[nicho]
hist_gem = st.session_state.hist_gemini[nicho]

# Exibe histórico
for msg in msgs:
    st.chat_message(msg["role"]).write(msg["content"])

# ── SAUDAÇÃO AUTOMÁTICA ao digitar o nome ────────────────────
nome = st.session_state.nome_usuario
if nome and not msgs and "saudacao_enviada" not in st.session_state:
    saudacao = (
        f"Olá, **{nome}**! 👋 Que bom ter você aqui!\n\n"
        f"Sou o assistente virtual do **Paulo Santos**, especialista em **Automação com IA** "
        f"para negócios como o seu.\n\n"
        f"Selecione o seu segmento acima e me conte sobre o seu negócio — "
        f"posso te ajudar a identificar onde a automação pode economizar tempo e gerar mais resultados. 🚀"
    )
    st.chat_message("assistant").write(saudacao)
    st.session_state.saudacao_enviada = True

# ── BUSCA INTERNET ────────────────────────────────────────────
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def buscar_internet(pergunta):
    try:
        r = tavily.search(query=pergunta, search_depth="advanced", max_results=5)
        return "\n".join(
            f"Título: {x['title']}\nConteúdo: {x['content']}\nFonte: {x['url']}"
            for x in r["results"]
        ).strip()
    except Exception as e:
        return f"Erro: {e}"

def precisa_buscar(p):
    sem = ["o que é","o que significa","como funciona","defina","explique",
           "escreva","traduza","corrija","piada","poema","qual a fórmula",
           "oi","olá","ola","bom dia","boa tarde","boa noite","tudo bem","obrigado"]
    return not any(s in p.lower() for s in sem)

# ── GEMINI ────────────────────────────────────────────────────
def responder_gemini(system_prompt, historico, mensagem_com_contexto):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        system_instruction=system_prompt
    )
    hist_fmt = []
    for h in historico[-12:]:
        role = "user" if h["role"] == "user" else "model"
        hist_fmt.append({"role": role, "parts": [h["content"]]})
    chat = model.start_chat(history=hist_fmt[:-1] if hist_fmt else [])
    return chat.send_message(mensagem_com_contexto).text

# ── GROQ (fallback) ───────────────────────────────────────────
def responder_groq(system_prompt, historico, mensagem_com_contexto):
    msgs_g = [{"role": "system", "content": system_prompt}]
    for h in historico[-12:]:
        msgs_g.append({"role": h["role"], "content": h["content"]})
    msgs_g.append({"role": "user", "content": mensagem_com_contexto})
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": msgs_g,
              "temperature": 0.5, "max_tokens": 1024},
        timeout=30
    )
    return resp.json()["choices"][0]["message"]["content"]

# ── CHAT INPUT ────────────────────────────────────────────────
entrada = st.chat_input(f"Pergunte sobre {config['badge'].lower()}...")

if entrada:
    # Salva primeira pergunta
    if not msgs:
        st.session_state.dados_lead["primeira_pergunta"] = entrada
        st.session_state.dados_lead["datetime"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.session_state.dados_lead["session_id"] = st.session_state.session_id
        st.session_state.dados_lead["nicho"] = nicho
        st.session_state.dados_lead["nome"] = st.session_state.nome_usuario

    st.chat_message("user").write(entrada)
    msgs.append({"role": "user", "content": entrada})
    hist_gem.append({"role": "user", "content": entrada})

    # Busca internet
    contexto = ""
    if precisa_buscar(entrada):
        with st.spinner("Buscando informações atualizadas..."):
            resultado = buscar_internet(entrada)
            if resultado:
                data = datetime.now().strftime("%d/%m/%Y")
                contexto = f"[INTERNET - {data}]\n{resultado}\n[FIM]\n\n"

    system = config["prompt"] + f"\nHoje: {datetime.now().strftime('%d/%m/%Y')}\nNome do usuário: {st.session_state.nome_usuario} — use o nome dele naturalmente na conversa."
    msg_completa = f"{contexto}Pergunta: {entrada}"

    resposta = None

    # Tenta Gemini
    if GEMINI_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando..."):
                resposta = responder_gemini(system, hist_gem[:-1], msg_completa)
        except Exception:
            pass

    # Fallback Groq
    if resposta is None and GROQ_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando..."):
                resposta = responder_groq(system, hist_gem[:-1], msg_completa)
        except Exception as e:
            resposta = f"Erro: {e}"

    if resposta is None:
        resposta = "Configure ao menos uma API key (Gemini ou Groq)."

    st.chat_message("assistant").write(resposta)
    msgs.append({"role": "assistant", "content": resposta})
    hist_gem.append({"role": "assistant", "content": resposta})

    total_msgs = len(msgs)
    st.session_state.dados_lead["total_msgs"] = total_msgs

    # ── Salva lead após 2ª mensagem com análise completa da IA ──
    if total_msgs >= 2 and not st.session_state.lead_salvo:
        with st.spinner(""):
            analise = analisar_lead_com_ia(nicho, msgs)
            tempo_min = round((datetime.now() - st.session_state.session_inicio).seconds / 60, 1)
            st.session_state.dados_lead.update({
                "cidade_estado": analise.get("cidade_estado", "Não informado"),
                "intencao":      analise.get("intencao", ""),
                "score":         analise.get("score", ""),
                "estagio":       analise.get("estagio", ""),
                "tempo_min":     tempo_min,
            })
            salvar_lead(st.session_state.dados_lead)
            st.session_state.lead_salvo = True

    # ── Detecta encerramento da conversa ──
    palavras_encerramento = ["tchau", "até mais", "ate mais", "até logo", "ate logo",
                             "obrigado", "obrigada", "valeu", "encerrar", "finalizar",
                             "foi ótimo", "foi otimo", "encerrando", "até", "xau"]
    if any(p in entrada.lower() for p in palavras_encerramento):
        st.session_state.conversa_encerrada = True

# ── BOTÃO DE ENCERRAR se conversa terminou ───────────────────
if st.session_state.get("conversa_encerrada") and msgs:
    st.markdown("""
<style>
.encerrar-box{background:#191e2b;border:1px solid #252d3d;border-radius:14px;padding:1.2rem 1.5rem;margin-top:1rem;text-align:center;position:relative;overflow:hidden}
.encerrar-box::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#0369a1,#38bdf8)}
.encerrar-titulo{font-size:0.95rem;color:#d4d0cb;margin-bottom:0.3rem;font-weight:600}
.encerrar-sub{font-size:0.83rem;color:#666;margin-bottom:1rem}
</style>
<div class="encerrar-box">
  <div class="encerrar-titulo">✅ Conversa encerrada</div>
  <div class="encerrar-sub">Obrigado pelo contato! Clique abaixo para iniciar uma nova conversa.</div>
</div>
""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 Nova conversa", type="primary", use_container_width=True):
            # Limpa tudo da sessão mantendo só o session_id
            sid = st.session_state.session_id
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.session_id = str(__import__('uuid').uuid4())[:8]
            st.rerun()
