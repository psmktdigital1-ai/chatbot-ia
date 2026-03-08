import streamlit as st
import google.generativeai as genai
from groq import Groq
from tavily import TavilyClient
from datetime import datetime
import os
import json
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Paulo AI", page_icon="✦", layout="centered")

AVATAR_B64 = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiMxZTJhM2EiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGQxNTIwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogIDwvZGVmcz4KICA8Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0idXJsKCNiZykiLz4KICA8cmVjdCB4PSI0OCIgeT0iNDIiIHdpZHRoPSIxMDQiIGhlaWdodD0iODIiIHJ4PSIxOCIgZmlsbD0iIzBmMWYzMCIgc3Ryb2tlPSIjMmE0YTZhIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDxyZWN0IHg9IjYwIiB5PSI2MiIgd2lkdGg9IjgwIiBoZWlnaHQ9IjI4IiByeD0iMTAiIGZpbGw9InJnYmEoNTYsODksMjQ4LDAuMTUpIiBzdHJva2U9IiMzOGJkZjgiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPGVsbGlwc2UgY3g9Ijc5IiBjeT0iNzYiIHJ4PSI4IiByeT0iNiIgZmlsbD0iIzBlYTVlOSIgb3BhY2l0eT0iMC45Ii8+CiAgPGVsbGlwc2UgY3g9IjEyMSIgY3k9Ijc2IiByeD0iOCIgcnk9IjYiIGZpbGw9IiMwZWE1ZTkiIG9wYWNpdHk9IjAuOSIvPgogIDxyZWN0IHg9IjY4IiB5PSI5OCIgd2lkdGg9IjY0IiBoZWlnaHQ9IjE2IiByeD0iNSIgZmlsbD0iIzBhMTgyNSIgc3Ryb2tlPSIjMWUzYTU1IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8cmVjdCB4PSI5NyIgeT0iMTAzIiB3aWR0aD0iOCIgaGVpZ2h0PSI2IiByeD0iMiIgZmlsbD0iIzM4YmRmOCIvPgogIDxwYXRoIGQ9Ik0zMCAyMDAgUTMyIDE1NSA1MiAxNDAgUTY4IDEzMiAxMDAgMTM0IFExMzIgMTMyIDE0OCAxNDAgUTE2OCAxNTUgMTcwIDIwMFoiIGZpbGw9IiMwZjFmMzAiLz4KPC9zdmc+"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[data-testid="stAppViewContainer"]{{background:#141414!important;font-family:'Inter',sans-serif;color:#ffffff}}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{{display:none!important}}
.block-container{{padding:0 1.5rem 5rem!important;max-width:740px!important}}
.header{{padding:3.5rem 0 2rem;display:flex;flex-direction:column;align-items:center}}
.avatar-circle{{width:120px;height:120px;border-radius:50%;overflow:hidden;border:2px solid #1e3a55;margin-bottom:1.2rem;box-shadow:0 0 0 4px rgba(56,189,248,0.08),0 8px 36px rgba(0,0,0,0.65)}}
.avatar-circle img{{width:100%;height:100%;object-fit:cover;display:block}}
.header-name{{font-family:'Instrument Serif',serif;font-size:2.8rem;font-weight:400;color:#ffffff;letter-spacing:-0.025em;line-height:1;margin-bottom:0.5rem}}
.header-desc{{font-size:1rem;color:#d0cdc8;text-align:center}}
.engine-badge{{display:inline-flex;align-items:center;gap:6px;margin-top:0.6rem;font-size:0.72rem;padding:3px 12px;border-radius:100px;letter-spacing:0.05em;font-family:monospace}}
.engine-gemini{{color:#4285f4;background:rgba(66,133,244,0.1);border:1px solid rgba(66,133,244,0.2)}}
.engine-groq{{color:#f97316;background:rgba(249,115,22,0.1);border:1px solid rgba(249,115,22,0.2)}}
.nicho-badge{{display:inline-flex;align-items:center;gap:6px;margin-top:0.5rem;font-size:0.78rem;color:#38bdf8;background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);padding:4px 12px;border-radius:100px;letter-spacing:0.05em}}
.online{{display:inline-flex;align-items:center;gap:6px;margin-top:0.6rem;font-size:0.85rem;color:#aaa}}
.online-dot{{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px rgba(34,197,94,0.5)}}
.sep{{width:36px;height:1px;background:#2e2e2e;margin:1.8rem auto 1.5rem}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:0.2rem 0!important}}[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li,[data-testid="stChatMessage"] span{{color:#ffffff!important}}[data-testid="stChatMessage"] a{{color:#38bdf8!important}}
[data-testid="stChatInput"]{{background:#ffffff!important;border:1px solid #dddddd!important;border-radius:14px!important}}
[data-testid="stChatInput"] textarea{{color:#111111!important;font-size:1.05rem!important}}[data-testid="stChatInput"] textarea::placeholder{{color:#888!important}}
[data-testid="stChatInputSubmitButton"] button{{background:#0ea5e9!important;border-radius:9px!important;border:none!important}}
::-webkit-scrollbar{{width:4px}}::-webkit-scrollbar-thumb{{background:#333;border-radius:999px}}
</style>
<div class="header">
  <div class="avatar-circle"><img src="{AVATAR_B64}" alt="Paulo AI"/></div>
  <div class="header-name">Paulo AI</div>
  <div class="header-desc">Assistente inteligente com acesso à internet em tempo real</div>
  <div class="online"><span class="online-dot"></span> disponível agora</div>
</div>
<div class="sep"></div>
""", unsafe_allow_html=True)

# ── API KEYS (Streamlit Secrets ou variáveis de ambiente) ────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY",   os.getenv("GROQ_API_KEY",   ""))
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY",  os.getenv("TAVILY_API_KEY", ""))

if not TAVILY_API_KEY:
    st.error("⚠️ Configure TAVILY_API_KEY em .streamlit/secrets.toml")
    st.stop()

if not GEMINI_API_KEY and not GROQ_API_KEY:
    st.error("⚠️ Configure ao menos GEMINI_API_KEY ou GROQ_API_KEY em .streamlit/secrets.toml")
    st.stop()

# ── CAPTURA DE LEADS ────────────────────────────────────────
def conectar_sheets():
    """Conecta ao Google Sheets via service account"""
    try:
        creds_json = st.secrets.get("GOOGLE_CREDS", "")
        if not creds_json:
            return None
        creds_dict = json.loads(creds_json)
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        return gc
    except Exception:
        return None

def registrar_lead(nicho, primeira_mensagem, resposta_ia):
    """Registra lead na planilha Google Sheets"""
    try:
        gc = conectar_sheets()
        if not gc:
            return  # silencioso se não configurado
        sheet_id = st.secrets.get("SHEET_ID", "")
        if not sheet_id:
            return
        sh = gc.open_by_key(sheet_id)
        try:
            ws = sh.worksheet("Leads Paulo AI")
        except Exception:
            ws = sh.add_worksheet("Leads Paulo AI", rows=1000, cols=10)
            ws.append_row(["Data/Hora", "Nicho", "Primeira Mensagem", "Resposta Paulo AI", "Sessão"])

        from datetime import datetime as dt
        session_id = st.session_state.get("session_id", "?")
        ws.append_row([
            dt.now().strftime("%d/%m/%Y %H:%M"),
            nicho,
            primeira_mensagem[:500],
            resposta_ia[:500],
            session_id
        ])
    except Exception:
        pass  # nunca quebra o chat por causa do sheets

# gera session_id único por visita
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())[:8]

# ── NICHOS ───────────────────────────────────────────────────
NICHOS = {
    "🏥 Clínica / Saúde": {
        "badge": "Especialista em Clínicas",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.

Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API · Google Ads · Meta Ads · Amazon Ads · VTEX Ads · Mercado Livre Ads

Serviços oferecidos:
- Automação de Cobranças e Documentos
- CRM + Cotação Automática para Corretoras
- Dashboard Unificado de Performance
- Automação de Agendamento e Clientes
- Lead Scoring com IA
- Análise de Dados e Relatório Estratégico
- Estratégia de Retail Media (Amazon, ML, Shopee, VTEX, Farma)
- Consultoria de E-commerce & Performance
- Chatbot Inteligente com IA
- App de Estatísticas e Dados
- Site / Portfólio Profissional
- Identidade Visual + Kit de Marca

REGRAS DE COMPORTAMENTO:
1. No PRIMEIRO contato (histórico vazio), apresente Paulo de forma calorosa e resumida — experiência, formação, segmentos atendidos e serviços. Finalize convidando o usuário a perguntar o que quiser. Exemplo de encerramento da apresentação: "Estou aqui para tirar qualquer dúvida do seu negócio e te ajudar com automação. Qual é a sua maior dor hoje? 😊"
2. Responda dúvidas com informações úteis, práticas e consultivas.
3. Ao identificar uma dor ou problema operacional, sugira como Paulo pode resolver com automação ou IA.
4. Ao final de respostas relevantes, inclua um CTA natural:
   "Quer falar diretamente com o Paulo? Entre em contato:"
   📱 WhatsApp: (11) 95113-1232
   📸 Instagram: @paulosantos.growthai
5. Nunca mencione empresa empregadora atual. Foque sempre na experiência, formação e resultados.
6. Seja consultivo, humano e direto. Nunca forçado na venda.
7. Responda sempre em português brasileiro.

NICHO: Clínicas, consultórios e espaços de saúde.
EXPERTISE: agendamento automático, lembretes WhatsApp, redução de faltas, pós-consulta automático, prontuários, relatórios de desempenho.
SERVIÇOS DE PAULO para clínicas: Automação de agendamento (R$ 900–2.000), Chatbot de atendimento, Dashboard de performance."""
    },
    "🏢 Corretora de Seguros": {
        "badge": "Especialista em Seguros",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.

Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API · Google Ads · Meta Ads · Amazon Ads · VTEX Ads · Mercado Livre Ads

Serviços oferecidos:
- Automação de Cobranças e Documentos
- CRM + Cotação Automática para Corretoras
- Dashboard Unificado de Performance
- Automação de Agendamento e Clientes
- Lead Scoring com IA
- Análise de Dados e Relatório Estratégico
- Estratégia de Retail Media (Amazon, ML, Shopee, VTEX, Farma)
- Consultoria de E-commerce & Performance
- Chatbot Inteligente com IA
- App de Estatísticas e Dados
- Site / Portfólio Profissional
- Identidade Visual + Kit de Marca

REGRAS DE COMPORTAMENTO:
1. No PRIMEIRO contato (histórico vazio), apresente Paulo de forma calorosa e resumida — experiência, formação, segmentos atendidos e serviços. Finalize convidando o usuário a perguntar o que quiser. Exemplo de encerramento da apresentação: "Estou aqui para tirar qualquer dúvida do seu negócio e te ajudar com automação. Qual é a sua maior dor hoje? 😊"
2. Responda dúvidas com informações úteis, práticas e consultivas.
3. Ao identificar uma dor ou problema operacional, sugira como Paulo pode resolver com automação ou IA.
4. Ao final de respostas relevantes, inclua um CTA natural:
   "Quer falar diretamente com o Paulo? Entre em contato:"
   📱 WhatsApp: (11) 95113-1232
   📸 Instagram: @paulosantos.growthai
5. Nunca mencione empresa empregadora atual. Foque sempre na experiência, formação e resultados.
6. Seja consultivo, humano e direto. Nunca forçado na venda.
7. Responda sempre em português brasileiro.

NICHO: Corretoras de seguros e planos.
EXPERTISE: cotação automática via WhatsApp, CRM de leads, follow-up de renovações, dashboard de pipeline de vendas.
SERVIÇOS DE PAULO para corretoras: CRM + Cotação Automática (principal case — 4x mais cotações), Chatbot inteligente, Dashboard de vendas."""
    },
    "📊 Escritório Contábil": {
        "badge": "Especialista em Contabilidade",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.

Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API · Google Ads · Meta Ads · Amazon Ads · VTEX Ads · Mercado Livre Ads

Serviços oferecidos:
- Automação de Cobranças e Documentos
- CRM + Cotação Automática para Corretoras
- Dashboard Unificado de Performance
- Automação de Agendamento e Clientes
- Lead Scoring com IA
- Análise de Dados e Relatório Estratégico
- Estratégia de Retail Media (Amazon, ML, Shopee, VTEX, Farma)
- Consultoria de E-commerce & Performance
- Chatbot Inteligente com IA
- App de Estatísticas e Dados
- Site / Portfólio Profissional
- Identidade Visual + Kit de Marca

REGRAS DE COMPORTAMENTO:
1. No PRIMEIRO contato (histórico vazio), apresente Paulo de forma calorosa e resumida — experiência, formação, segmentos atendidos e serviços. Finalize convidando o usuário a perguntar o que quiser. Exemplo de encerramento da apresentação: "Estou aqui para tirar qualquer dúvida do seu negócio e te ajudar com automação. Qual é a sua maior dor hoje? 😊"
2. Responda dúvidas com informações úteis, práticas e consultivas.
3. Ao identificar uma dor ou problema operacional, sugira como Paulo pode resolver com automação ou IA.
4. Ao final de respostas relevantes, inclua um CTA natural:
   "Quer falar diretamente com o Paulo? Entre em contato:"
   📱 WhatsApp: (11) 95113-1232
   📸 Instagram: @paulosantos.growthai
5. Nunca mencione empresa empregadora atual. Foque sempre na experiência, formação e resultados.
6. Seja consultivo, humano e direto. Nunca forçado na venda.
7. Responda sempre em português brasileiro.

NICHO: Escritórios de contabilidade e assessoria fiscal.
EXPERTISE: cobrança automática de documentos, DRE automático, lembretes de prazos fiscais, comunicação com clientes via WhatsApp, organização de arquivos.
SERVIÇOS DE PAULO para contábeis: Automação de cobranças e documentos (principal case — −80% do tempo), Relatórios automáticos, Chatbot de atendimento."""
    },
    "✂️ Barbearia / Estética": {
        "badge": "Especialista em Barbearias",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.

Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API · Google Ads · Meta Ads · Amazon Ads · VTEX Ads · Mercado Livre Ads

Serviços oferecidos:
- Automação de Cobranças e Documentos
- CRM + Cotação Automática para Corretoras
- Dashboard Unificado de Performance
- Automação de Agendamento e Clientes
- Lead Scoring com IA
- Análise de Dados e Relatório Estratégico
- Estratégia de Retail Media (Amazon, ML, Shopee, VTEX, Farma)
- Consultoria de E-commerce & Performance
- Chatbot Inteligente com IA
- App de Estatísticas e Dados
- Site / Portfólio Profissional
- Identidade Visual + Kit de Marca

REGRAS DE COMPORTAMENTO:
1. No PRIMEIRO contato (histórico vazio), apresente Paulo de forma calorosa e resumida — experiência, formação, segmentos atendidos e serviços. Finalize convidando o usuário a perguntar o que quiser. Exemplo de encerramento da apresentação: "Estou aqui para tirar qualquer dúvida do seu negócio e te ajudar com automação. Qual é a sua maior dor hoje? 😊"
2. Responda dúvidas com informações úteis, práticas e consultivas.
3. Ao identificar uma dor ou problema operacional, sugira como Paulo pode resolver com automação ou IA.
4. Ao final de respostas relevantes, inclua um CTA natural:
   "Quer falar diretamente com o Paulo? Entre em contato:"
   📱 WhatsApp: (11) 95113-1232
   📸 Instagram: @paulosantos.growthai
5. Nunca mencione empresa empregadora atual. Foque sempre na experiência, formação e resultados.
6. Seja consultivo, humano e direto. Nunca forçado na venda.
7. Responda sempre em português brasileiro.

NICHO: Barbearias, salões e estúdios de estética.
EXPERTISE: agendamento automático, lembretes de confirmação, redução de no-show, programa de fidelidade, reativação de clientes inativos.
SERVIÇOS DE PAULO para barbearias: Automação de agendamento, Chatbot WhatsApp, Dashboard de faturamento por barbeiro/serviço."""
    },
    "🛒 E-commerce / Loja": {
        "badge": "Especialista em E-commerce",
        "prompt": """IDENTIDADE — Paulo Santos (Growth AI):
Paulo Santos é especialista em Dados, IA e Automação com anos de experiência no mercado digital. Pós-graduado em Ciências de Dados & Inteligência Artificial, já trabalhou com empresas de diferentes segmentos aplicando automação inteligente com n8n, Python, GPT-4 e integração com WhatsApp para resolver problemas reais de operação e crescimento.

Segmentos atendidos: clínicas, corretoras de seguros, escritórios contábeis, barbearias e e-commerce.

Tecnologias: n8n · Python · SQL · GPT-4 · Power BI · Looker Studio · WhatsApp API · Google Ads · Meta Ads · Amazon Ads · VTEX Ads · Mercado Livre Ads

Serviços oferecidos:
- Automação de Cobranças e Documentos
- CRM + Cotação Automática para Corretoras
- Dashboard Unificado de Performance
- Automação de Agendamento e Clientes
- Lead Scoring com IA
- Análise de Dados e Relatório Estratégico
- Estratégia de Retail Media (Amazon, ML, Shopee, VTEX, Farma)
- Consultoria de E-commerce & Performance
- Chatbot Inteligente com IA
- App de Estatísticas e Dados
- Site / Portfólio Profissional
- Identidade Visual + Kit de Marca

REGRAS DE COMPORTAMENTO:
1. No PRIMEIRO contato (histórico vazio), apresente Paulo de forma calorosa e resumida — experiência, formação, segmentos atendidos e serviços. Finalize convidando o usuário a perguntar o que quiser. Exemplo de encerramento da apresentação: "Estou aqui para tirar qualquer dúvida do seu negócio e te ajudar com automação. Qual é a sua maior dor hoje? 😊"
2. Responda dúvidas com informações úteis, práticas e consultivas.
3. Ao identificar uma dor ou problema operacional, sugira como Paulo pode resolver com automação ou IA.
4. Ao final de respostas relevantes, inclua um CTA natural:
   "Quer falar diretamente com o Paulo? Entre em contato:"
   📱 WhatsApp: (11) 95113-1232
   📸 Instagram: @paulosantos.growthai
5. Nunca mencione empresa empregadora atual. Foque sempre na experiência, formação e resultados.
6. Seja consultivo, humano e direto. Nunca forçado na venda.
7. Responda sempre em português brasileiro.

NICHO: Lojas virtuais, marcas e operações de e-commerce.
EXPERTISE: Retail Media (Amazon Ads, ML Ads, Shopee, VTEX Ads), análise de SKU e ROAS, automação de campanhas, dashboards de performance multicanal.
SERVIÇOS DE PAULO para e-commerce: Estratégia de Retail Media, Dashboard unificado de performance, Consultoria de e-commerce & mídia paga."""
    },
    "🤖 Geral": {
        "badge": "Chat Geral",
        "prompt": """Você é Paulo AI, um assistente inteligente geral — como o ChatGPT ou Gemini.
Responda qualquer tipo de pergunta: ciência, história, tecnologia, negócios, curiosidades, receitas, viagens, saúde, cultura, entretenimento, idiomas, matemática, programação e muito mais.
Sem restrição de tema. Seja útil, claro, completo e direto.
Responda sempre em português brasileiro, a menos que o usuário escreva em outro idioma — nesse caso responda no idioma dele.
Cite fontes quando usar dados da internet."""
    }
}

# ── SELETOR DE NICHO ─────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:1.2rem;padding:0 0.5rem">
  <div style="font-size:1.05rem;color:#ffffff;font-weight:600;margin-bottom:0.4rem">
    Qual é o seu segmento?
  </div>
  <div style="font-size:0.88rem;color:#b0b0b0;line-height:1.6">
    Selecione o nicho do seu negócio para uma conversa especializada —
    ou escolha <strong style="color:#b0a898">🤖 Geral</strong> para dúvidas livres sobre automação, dados e IA.
  </div>
</div>
""", unsafe_allow_html=True)

nicho = st.selectbox("Área:", list(NICHOS.keys()), label_visibility="collapsed")
config = NICHOS[nicho]
st.markdown(f'<div style="text-align:center;margin-bottom:1rem"><span class="nicho-badge">✦ {config["badge"]}</span></div>', unsafe_allow_html=True)

# ── ESTADO ───────────────────────────────────────────────────
for key in ["msgs", "hist_gemini", "engine_usado"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key != "engine_usado" else "gemini"

for key in ["msgs", "hist_gemini"]:
    if nicho not in st.session_state[key]:
        st.session_state[key][nicho] = []

msgs       = st.session_state.msgs[nicho]
hist_gem   = st.session_state.hist_gemini[nicho]

for msg in msgs:
    st.chat_message(msg["role"]).write(msg["content"])

# ── BUSCA ────────────────────────────────────────────────────
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
           "escreva","traduza","corrija","piada","poema","qual a fórmula"]
    return not any(s in p.lower() for s in sem)

# ── GEMINI ───────────────────────────────────────────────────
def responder_gemini(system_prompt, historico, mensagem_com_contexto):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        system_instruction=system_prompt
    )
    # converte histórico para formato Gemini
    hist_formatado = []
    for h in historico[-12:]:
        role = "user" if h["role"] == "user" else "model"
        hist_formatado.append({"role": role, "parts": [h["content"]]})

    chat = model.start_chat(history=hist_formatado[:-1] if hist_formatado else [])
    response = chat.send_message(mensagem_com_contexto)
    return response.text

# ── GROQ (fallback) ──────────────────────────────────────────
def responder_groq(system_prompt, historico, mensagem_com_contexto):
    client = Groq(api_key=GROQ_API_KEY)
    msgs_groq = [{"role": "system", "content": system_prompt}]
    for h in historico[-12:]:
        msgs_groq.append({"role": h["role"], "content": h["content"]})
    msgs_groq.append({"role": "user", "content": mensagem_com_contexto})
    resp = client.chat.completions.create(
        messages=msgs_groq,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_tokens=1024
    )
    return resp.choices[0].message.content

# ── CHAT PRINCIPAL ───────────────────────────────────────────
entrada = st.chat_input(f"Pergunte sobre {config['badge'].lower()}...")

if entrada:
    st.chat_message("user").write(entrada)
    msgs.append({"role": "user", "content": entrada})
    hist_gem.append({"role": "user", "content": entrada})

    # busca
    contexto = ""
    if precisa_buscar(entrada):
        with st.spinner("Buscando informações atualizadas..."):
            resultado = buscar_internet(entrada)
            if resultado:
                data = datetime.now().strftime("%d/%m/%Y")
                contexto = f"[INTERNET - {data}]\n{resultado}\n[FIM]\n\n"

    system = config["prompt"] + f"\nHoje: {datetime.now().strftime('%d/%m/%Y')}"
    msg_completa = f"{contexto}Pergunta: {entrada}"

    resposta = None
    engine   = "gemini"

    # tenta Gemini primeiro
    if GEMINI_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando..."):
                resposta = responder_gemini(system, hist_gem[:-1], msg_completa)
            engine = "gemini"
        except Exception as e:
            pass  # fallback silencioso para Groq

    # fallback Groq
    if resposta is None and GROQ_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando (Groq)..."):
                resposta = responder_groq(system, hist_gem[:-1], msg_completa)
            engine = "groq"
        except Exception as e:
            resposta = f"Erro em ambos os modelos: {e}"
            engine = "erro"

    if resposta is None:
        resposta = "Configure ao menos uma API key (Gemini ou Groq)."

    st.chat_message("assistant").write(resposta)
    msgs.append({"role": "assistant", "content": resposta})
    hist_gem.append({"role": "assistant", "content": resposta})

    # captura lead no primeiro contato
    if len(msgs) <= 2:
        registrar_lead(nicho, entrada, resposta)