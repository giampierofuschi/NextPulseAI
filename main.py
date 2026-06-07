"""
main.py — AI Sales Assistant · Engine SpA
Deal Cockpit — interfaccia strutturata per il team commerciale

Avvio:
    streamlit run main.py

Prerequisito:
    python index.py   ← esegui una volta sola per costruire il vector store
"""

import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from retriever import Retriever
from parametrizer import Parametrizer
from intent_classifier import IntentClassifier
from prompt_builder import PromptBuilder

# ════════════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════════════

# Carica la chiave da variabile d'ambiente o da st.secrets
# GROQ_API_KEY = 
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

TOP_K = 5

STAGE_ORDER = ["Lead", "Discovery", "Demo", "Gara", "Offerta", "Negoziazione"]

PRODOTTI_OPTIONS = ["Speed Cam", "OCR / ZTL", "Red Light", "Analytics AI", "Backoffice", "Mobile Unit"]
PRIORITA_OPTIONS = ["Sicurezza", "Compliance", "Riduzione traffico", "Revenue", "Riduzione costi"]
COMPLIANCE_OPTIONS = ["GDPR", "ANAC", "Omologazione MIT", "Cybersecurity NIS2"]
SEGMENTI = ["", "Comune", "Provincia", "Polizia Locale", "Gestore autostradale", "Smart City", "Azienda trasporti"]
STAGE_OPTIONS = [""] + STAGE_ORDER
DEPLOY_OPTIONS = ["", "Cloud", "On Premise", "Hybrid"]

# ════════════════════════════════════════════════════════════════════════════
# RISORSE — caricate una volta sola (cache Streamlit)
# ════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_groq(api_key: str):
    if not api_key:
        return None
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=api_key,
    )

@st.cache_resource
def load_retriever():
    try:
        return Retriever()
    except Exception:
        return None

@st.cache_resource
def load_parametrizer():
    return Parametrizer()

@st.cache_resource
def load_classifier():
    return IntentClassifier()

@st.cache_resource
def load_prompt_builder():
    return PromptBuilder()

# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def get_deal_from_session() -> dict:
    return {
        "cliente":    st.session_state.get("f_cliente", ""),
        "segmento":   st.session_state.get("f_segmento", ""),
        "stage":      st.session_state.get("f_stage", ""),
        "budget":     st.session_state.get("f_budget", ""),
        "deploy":     st.session_state.get("f_deploy", ""),
        "competitor": st.session_state.get("f_competitor", ""),
        "prodotti":   st.session_state.get("sel_prodotti", []),
        "priorita":   st.session_state.get("sel_priorita", []),
        "compliance": st.session_state.get("sel_compliance", []),
        "note":       st.session_state.get("f_note", ""),
    }

def format_budget(val: str) -> str:
    try:
        return f"€ {int(val):,}".replace(",", ".")
    except Exception:
        return val

def stage_progress(stage: str) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError:
        return -1

def retrieve_context(query: str, retriever) -> tuple[str, list]:
    if retriever is None or not query.strip():
        return "", []
    try:
        results = retriever.search(query, top_k=TOP_K)
        parts, sources = [], []
        for i, r in enumerate(results, 1):
            text = r.get("text", "").strip()
            fname = r.get("file_name", "fonte sconosciuta")
            score = r.get("score", 0.0)
            if not text:
                continue
            if fname not in sources:
                sources.append(fname)
            parts.append(f"[Fonte {i} — {fname} · rilevanza {score:.2f}]\n{text}")
        return "\n\n---\n\n".join(parts), sources
    except Exception:
        return "", []

def call_llm(llm, system: str, user: str) -> str:
    if llm is None:
        return "⚠️ API key Groq non configurata. Aggiungi GROQ_API_KEY in .streamlit/secrets.toml o direttamente nel codice."
    try:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        err = str(e)
        if "401" in err or "authentication" in err.lower() or "api_key" in err.lower():
            return "⚠️ API key non valida o scaduta. Verifica la GROQ_API_KEY in secrets.toml."
        if "connection" in err.lower() or "network" in err.lower():
            return "⚠️ Errore di connessione a Groq. Controlla la connessione internet e riprova."
        return f"⚠️ Errore nella generazione: {err}"

# ════════════════════════════════════════════════════════════════════════════
# CSS GLOBALE
# ════════════════════════════════════════════════════════════════════════════

GLOBAL_CSS = """
<style>
/* ── reset & base ── */
[data-testid="stMain"] { padding-top: 0.5rem !important; }
div[data-testid="column"] { padding: 0 6px !important; }

/* ── pannelli ── */
.eng-panel {
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 10px;
}
.eng-panel-title {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--text-color);
    opacity: 0.5;
    margin-bottom: .7rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── section card output ── */
.sec-card {
    background: rgba(128,128,128,0.07);
    border-radius: 8px;
    padding: .85rem 1rem;
    border-left: 3px solid rgba(128,128,128,0.25);
    margin-bottom: 8px;
}
.sec-card.norm  { border-left-color: #378ADD; }
.sec-card.conf  { border-left-color: #1D9E75; }
.sec-card.risk  { border-left-color: #E24B4A; }
.sec-card.coach { border-left-color: #BA7517; }
.sec-card.steps { border-left-color: #7F77DD; }
.sec-head {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--text-color);
    opacity: 0.5;
    margin-bottom: .45rem;
}
.sec-body {
    font-size: 13px;
    color: var(--text-color);
    line-height: 1.65;
}
.sec-source {
    font-size: 10px;
    color: var(--text-color);
    opacity: 0.4;
    margin-top: 5px;
    font-style: italic;
}

/* ── badge ── */
.badge {
    display: inline-block;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 600;
    margin-left: 6px;
}
.badge-ok   { background: #1D9E7522; color: #1D9E75; border: 1px solid #1D9E7544; }
.badge-warn { background: #BA751722; color: #BA7517; border: 1px solid #BA751744; }
.badge-err  { background: #E24B4A22; color: #E24B4A; border: 1px solid #E24B4A44; }
.badge-info { background: #378ADD22; color: #378ADD; border: 1px solid #378ADD44; }

/* ── progress bar stage ── */
.stage-bar { display: flex; gap: 4px; margin-top: 5px; }
.stage-seg {
    flex: 1;
    height: 4px;
    border-radius: 2px;
    background: rgba(128,128,128,0.2);
}
.stage-seg.done   { background: #1D9E75; }
.stage-seg.active { background: #378ADD; }

/* ── context pills ── */
.ctx-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 20px;
    background: #378ADD22;
    color: #378ADD;
    border: 1px solid #378ADD44;
    margin-right: 4px;
    margin-bottom: 4px;
}

/* ── header ── */
.cockpit-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .6rem 1.2rem .6rem;
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 12px;
    margin-bottom: 10px;
}
.cockpit-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    display: flex;
    align-items: center;
    gap: 10px;
}
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Deal Cockpit · Engine SpA",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# — carica risorse —
llm           = load_groq(GROQ_API_KEY)
retriever     = load_retriever()
param         = load_parametrizer()
classifier    = load_classifier()
prompt_builder = load_prompt_builder()

# — init session state —
defaults = {
    "f_cliente": "",
    "f_segmento": "",
    "f_stage": "",
    "f_budget": "",
    "f_deploy": "",
    "f_competitor": "",
    "f_note": "",
    "sel_prodotti": [],
    "sel_priorita": [],
    "sel_compliance": [],
    "analysis_result": None,
    "chat_messages": [],
    "active_action": None,
    "action_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════

vs_ok = retriever is not None and hasattr(retriever, "index")
vs_count = retriever.index.ntotal if vs_ok else 0

# ─── Avviso API key mancante ───
if not GROQ_API_KEY:
    st.error(
        "🔑 API key Groq non trovata. "
        "Crea .streamlit/secrets.toml con: GROQ_API_KEY = 'gsk_...' "
        "oppure incolla la chiave alla riga 27 del codice."
    )

st.markdown(f"""
<div class="cockpit-header">
  <div class="cockpit-title">
    🚦 Deal Cockpit
    <span style="font-size:12px;font-weight:400;opacity:0.5;">Engine SpA · Sales Intelligence</span>
  </div>
  <div>
    {'<span class="badge badge-ok">✓ Vector store attivo · ' + str(vs_count) + ' chunk</span>'
     if vs_ok else
     '<span class="badge badge-err">✗ Vector store non trovato — esegui: python index.py</span>'}
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LAYOUT: 3 COLONNE
# ════════════════════════════════════════════════════════════════════════════

col_left, col_center, col_right = st.columns([1, 2.2, 0.9], gap="small")

# ════════════════════════════════════════════════════════════════════════════
# COLONNA SINISTRA — DEAL BRIEFING
# ════════════════════════════════════════════════════════════════════════════

with col_left:
    st.markdown('<div class="eng-panel">', unsafe_allow_html=True)
    st.markdown('<div class="eng-panel-title">🏢 Deal Briefing</div>', unsafe_allow_html=True)

    st.session_state.f_cliente   = st.text_input("Cliente / Ente", value=st.session_state.f_cliente,
                                                   placeholder="Es. Comune di Milano...", label_visibility="visible")
    st.session_state.f_segmento  = st.selectbox("Segmento", SEGMENTI,
                                                  index=SEGMENTI.index(st.session_state.f_segmento)
                                                  if st.session_state.f_segmento in SEGMENTI else 0)
    st.session_state.f_stage     = st.selectbox("Fase commerciale", STAGE_OPTIONS,
                                                  index=STAGE_OPTIONS.index(st.session_state.f_stage)
                                                  if st.session_state.f_stage in STAGE_OPTIONS else 0)

    # Barra avanzamento stage
    if st.session_state.f_stage:
        idx = stage_progress(st.session_state.f_stage)
        segs = ""
        for i in range(len(STAGE_ORDER)):
            cls = "done" if i < idx else ("active" if i == idx else "")
            segs += f'<div class="stage-seg {cls}"></div>'
        st.markdown(f'<div class="stage-bar">{segs}</div>', unsafe_allow_html=True)

    st.markdown("**Prodotti di interesse**")
    st.session_state.sel_prodotti = st.multiselect(
        "Prodotti", PRODOTTI_OPTIONS,
        default=st.session_state.sel_prodotti,
        label_visibility="collapsed"
    )

    st.markdown("**Priorità cliente**")
    st.session_state.sel_priorita = st.multiselect(
        "Priorità", PRIORITA_OPTIONS,
        default=st.session_state.sel_priorita,
        label_visibility="collapsed"
    )

    st.session_state.f_budget    = st.text_input("Budget indicativo (€)",
                                                   value=st.session_state.f_budget,
                                                   placeholder="Es. 300000")
    st.session_state.f_deploy    = st.selectbox("Deployment", DEPLOY_OPTIONS,
                                                  index=DEPLOY_OPTIONS.index(st.session_state.f_deploy)
                                                  if st.session_state.f_deploy in DEPLOY_OPTIONS else 0)

    st.markdown("**Compliance richiesta**")
    st.session_state.sel_compliance = st.multiselect(
        "Compliance", COMPLIANCE_OPTIONS,
        default=st.session_state.sel_compliance,
        label_visibility="collapsed"
    )

    st.session_state.f_competitor = st.text_input("Competitor menzionato",
                                                    value=st.session_state.f_competitor,
                                                    placeholder="Es. Jenoptik, Swarco...")
    st.session_state.f_note       = st.text_area("Note aggiuntive",
                                                   value=st.session_state.f_note,
                                                   placeholder="Stakeholder chiave, urgenze, vincoli...",
                                                   height=80)

    st.markdown("</div>", unsafe_allow_html=True)

    run = st.button("⚡ Analizza deal", use_container_width=True, type="primary")
    if st.button("🗑️ Reset", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# ANALISI — eseguita al click (o quando arriva un'azione rapida)
# ════════════════════════════════════════════════════════════════════════════

if run:
    deal = get_deal_from_session()

    # Validazione minima
    if not deal["cliente"] and not deal["segmento"] and not deal["prodotti"]:
        st.session_state.analysis_result = {"error": "Compila almeno Cliente, Segmento o Prodotti prima di analizzare."}
    else:
        with st.spinner("Analisi in corso..."):
            # 1. RAG retrieval
            rag_query = prompt_builder.build_rag_query(deal)
            rag_context, sources = retrieve_context(rag_query, retriever)

            # 2. Classificazione intento
            query_text = prompt_builder.deal_to_text(deal)
            intent = classifier.classify(query_text)
            intent_instructions = classifier.get_response_instructions(intent["key"])

            # 3. Validazione parametri
            structured = param.extract_parameters(query_text)
            validation_errors = param.validate(structured)

            # 4. Chiama LLM per ogni sezione
            system_prompt = prompt_builder.get_system_prompt()

            sections = {}

            # Configurazione tecnica
            cfg_prompt = prompt_builder.section_prompt("configurazione", deal, rag_context)
            sections["configurazione"] = call_llm(llm, system_prompt, cfg_prompt)

            # Normativa
            norm_prompt = prompt_builder.section_prompt("normativa", deal, rag_context)
            sections["normativa"] = call_llm(llm, system_prompt, norm_prompt)

            # Rischi
            risk_prompt = prompt_builder.section_prompt("rischi", deal, rag_context)
            sections["rischi"] = call_llm(llm, system_prompt, risk_prompt)

            # Sales coaching (solo se c'è un competitor)
            if deal["competitor"]:
                coach_prompt = prompt_builder.section_prompt("coaching", deal, rag_context)
                sections["coaching"] = call_llm(llm, system_prompt, coach_prompt)

            # Prossimi passi
            steps_prompt = prompt_builder.section_prompt("prossimi_passi", deal, rag_context)
            sections["prossimi_passi"] = call_llm(llm, system_prompt, steps_prompt)

            st.session_state.analysis_result = {
                "deal": deal,
                "sections": sections,
                "sources": sources,
                "intent": intent,
                "validation": validation_errors,
            }
            st.session_state.active_action = None
            st.session_state.action_result = None

# ════════════════════════════════════════════════════════════════════════════
# COLONNA CENTRALE — OUTPUT INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════

with col_center:

    result = st.session_state.analysis_result

    if result is None and st.session_state.active_action is None:
        # Empty state
        st.markdown("""
        <div class="eng-panel" style="min-height:500px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;text-align:center">
          <div style="font-size:36px;opacity:.3">📊</div>
          <div style="font-size:14px;opacity:0.5;max-width:280px;line-height:1.6">
            Compila il briefing e premi <b>Analizza deal</b> per generare l'intelligence strutturata.
          </div>
          <div style="font-size:12px;opacity:0.35;margin-top:8px">
            Oppure usa le Quick Actions sulla destra per azioni specifiche.
          </div>
        </div>
        """, unsafe_allow_html=True)

    elif result and "error" in result:
        st.error(result["error"])

    elif result and "sections" in result:
        deal = result["deal"]
        sections = result["sections"]
        sources = result["sources"]
        intent = result["intent"]
        validation = result["validation"]

        # Context pills
        pills = ""
        if deal["cliente"]:   pills += f'<span class="ctx-pill">🏛 {deal["cliente"]}</span>'
        if deal["stage"]:     pills += f'<span class="ctx-pill">📍 {deal["stage"]}</span>'
        if deal["budget"]:    pills += f'<span class="ctx-pill">💶 {format_budget(deal["budget"])}</span>'
        if deal["deploy"]:    pills += f'<span class="ctx-pill">☁ {deal["deploy"]}</span>'
        if deal["segmento"]:  pills += f'<span class="ctx-pill">🏷 {deal["segmento"]}</span>'
        if pills:
            st.markdown(f'<div style="margin-bottom:10px">{pills}</div>', unsafe_allow_html=True)

        # Intent badge
        badge_map = {
            "normativa":       ("badge-info",  "⚖️ Normativa e compliance"),
            "configurazione":  ("badge-ok",    "⚙️ Configurazione tecnica"),
            "tender":          ("badge-warn",  "📋 Gara d'appalto"),
            "sales_coaching":  ("badge-err",   "🎯 Sales coaching"),
            "deal_context":    ("badge-info",  "🏢 Contesto deal"),
        }
        bc, bl = badge_map.get(intent["key"], ("badge-info", f"💬 {intent['label']}"))
        st.markdown(f'<span class="badge {bc}">{bl}</span>', unsafe_allow_html=True)

        # Errori di validazione
        if validation:
            with st.expander("⚠️ Alert di validazione", expanded=True):
                for v in validation:
                    st.markdown(v)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── SEZIONE: CONFIGURAZIONE ──
        st.markdown(f"""
        <div class="sec-card conf">
          <div class="sec-head">⚙️ Configurazione consigliata</div>
          <div class="sec-body">{sections.get('configurazione','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── SEZIONE: NORMATIVA ──
        has_anac_warn = "Gara" in deal.get("stage", "") and "ANAC" not in deal.get("compliance", [])
        norm_badge = '<span class="badge badge-err">⚠ ANAC mancante</span>' if has_anac_warn else ""
        st.markdown(f"""
        <div class="sec-card norm">
          <div class="sec-head">⚖️ Normativa applicabile {norm_badge}</div>
          <div class="sec-body">{sections.get('normativa','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── SEZIONE: RISCHI ──
        st.markdown(f"""
        <div class="sec-card risk">
          <div class="sec-head">🔴 Rischi e attenzioni</div>
          <div class="sec-body">{sections.get('rischi','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── SEZIONE: COACHING (solo se competitor) ──
        if "coaching" in sections:
            st.markdown(f"""
            <div class="sec-card coach">
              <div class="sec-head">🎯 Positioning vs {deal['competitor']}</div>
              <div class="sec-body">{sections['coaching']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── SEZIONE: PROSSIMI PASSI ──
        st.markdown(f"""
        <div class="sec-card steps">
          <div class="sec-head">📌 Prossimi passi consigliati</div>
          <div class="sec-body">{sections.get('prossimi_passi','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Fonti
        if sources:
            with st.expander("📄 Fonti utilizzate dal vector store"):
                for s in sources:
                    st.caption(f"• {s}")

    # ── OUTPUT AZIONE RAPIDA ──
    if st.session_state.active_action and st.session_state.action_result:
        action_labels = {
            "offerta":     "📄 Bozza offerta",
            "gara":        "📋 Analisi gara",
            "obiezioni":   "💬 Gestione obiezioni",
            "competitor":  "⚔️ Positioning competitor",
            "normativa":   "⚖️ Riferimenti normativi",
            "stakeholder": "👥 Mappa stakeholder",
        }
        label = action_labels.get(st.session_state.active_action, "Risultato")
        st.markdown(f"""
        <div class="sec-card steps" style="margin-top:12px">
          <div class="sec-head">{label}</div>
          <div class="sec-body">{st.session_state.action_result}</div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # CHAT DRAWER (collassabile, secondario)
    # ════════════════════════════════════════════════
    with st.expander("💬 Assistente conversazionale (follow-up)", expanded=False):
        st.caption("Usa questo pannello solo per domande di approfondimento specifiche.")

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Domanda di follow-up..."):
            st.session_state.chat_messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            deal = get_deal_from_session()
            ctx_text = prompt_builder.deal_to_text(deal)
            rag_ctx, _ = retrieve_context(chat_input, retriever)

            follow_up_prompt = f"""
CONTESTO DEAL CORRENTE:
{ctx_text}

DOCUMENTI RECUPERATI:
{rag_ctx if rag_ctx else 'Nessun documento rilevante trovato.'}

DOMANDA FOLLOW-UP: {chat_input}
"""
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    answer = call_llm(llm, prompt_builder.get_system_prompt(), follow_up_prompt)
                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})

# ════════════════════════════════════════════════════════════════════════════
# COLONNA DESTRA — QUICK ACTIONS + PANNELLO STATO
# ════════════════════════════════════════════════════════════════════════════

with col_right:

    # Quick Actions
    st.markdown('<div class="eng-panel">', unsafe_allow_html=True)
    st.markdown('<div class="eng-panel-title">⚡ Quick Actions</div>', unsafe_allow_html=True)

    deal = get_deal_from_session()

    ACTION_CONFIG = [
        ("offerta",     "📄", "Genera bozza offerta"),
        ("gara",        "📋", "Analisi capitolato gara"),
        ("obiezioni",   "💬", "Gestione obiezioni"),
        ("competitor",  "⚔️", "Positioning vs competitor"),
        ("normativa",   "⚖️", "Riferimenti normativi"),
        ("stakeholder", "👥", "Mappa stakeholder"),
    ]

    for action_key, icon, label in ACTION_CONFIG:
        if st.button(f"{icon} {label}", key=f"qa_{action_key}", use_container_width=True):
            with st.spinner(f"{label}..."):
                deal = get_deal_from_session()
                rag_query = prompt_builder.build_rag_query(deal)
                rag_context, _ = retrieve_context(rag_query, retriever)
                action_prompt = prompt_builder.action_prompt(action_key, deal, rag_context)
                result_text = call_llm(llm, prompt_builder.get_system_prompt(), action_prompt)
                st.session_state.active_action = action_key
                st.session_state.action_result = result_text
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Pannello stato deal
    st.markdown('<div class="eng-panel">', unsafe_allow_html=True)
    st.markdown('<div class="eng-panel-title">🏢 Stato deal</div>', unsafe_allow_html=True)

    deal = get_deal_from_session()
    ctx_lines = []
    if deal["cliente"]:             ctx_lines.append(f"**Cliente:** {deal['cliente']}")
    if deal["segmento"]:            ctx_lines.append(f"**Segmento:** {deal['segmento']}")
    if deal["stage"]:               ctx_lines.append(f"**Stage:** {deal['stage']}")
    if deal["budget"]:              ctx_lines.append(f"**Budget:** {format_budget(deal['budget'])}")
    if deal["prodotti"]:            ctx_lines.append(f"**Prodotti:** {', '.join(deal['prodotti'])}")
    if deal["compliance"]:          ctx_lines.append(f"**Compliance:** {', '.join(deal['compliance'])}")
    if deal["competitor"]:          ctx_lines.append(f"**Competitor:** {deal['competitor']}")
    if deal["deploy"]:              ctx_lines.append(f"**Deploy:** {deal['deploy']}")

    if ctx_lines:
        for line in ctx_lines:
            st.markdown(f'<div style="font-size:12px;line-height:1.9">{line}</div>',
                        unsafe_allow_html=True)
    else:
        st.caption("Nessun dato ancora inserito.")

    # Intent live
    if st.session_state.analysis_result and "intent" in st.session_state.analysis_result:
        intent = st.session_state.analysis_result["intent"]
        st.markdown("<hr style='border:none;border-top:1px solid rgba(128,128,128,0.2);margin:.7rem 0'>", unsafe_allow_html=True)
        st.markdown('<div class="eng-panel-title">🧠 Intent rilevato</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-info">{intent["emoji"]} {intent["label"]}</span>',
                    unsafe_allow_html=True)
        if intent.get("matches"):
            st.caption(f"keyword: {', '.join(intent['matches'][:4])}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Sistema info
    st.markdown('<div class="eng-panel">', unsafe_allow_html=True)
    st.markdown('<div class="eng-panel-title">🔧 Sistema</div>', unsafe_allow_html=True)
    st.caption(f"Modello: llama-3.3-70b-versatile")
    st.caption(f"Vector store: {'attivo (' + str(vs_count) + ' chunk)' if vs_ok else 'non disponibile'}")
    st.caption(f"RAG top-k: {TOP_K}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Engine SpA · Gruppo Zenita\nDeal Cockpit v1.0")
