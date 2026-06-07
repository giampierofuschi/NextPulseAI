import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from retriever import Retriever
from parametrizer import Parametrizer
from intent_classifier import IntentClassifier
from prompt_builder import PromptBuilder

#api-key
GROQ_API_KEY =
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

#top_k indica i top 5 chunk
TOP_K = 10
PRODOTTI_OPTIONS = ["", "Controllo Velocità", "ZTL", "Infrazione semaforo", "Analytics per mobilità urbana"]
SEGMENTI = ["", "Comune", "Provincia", "Polizia Locale", "Gestore autostradale", "Smart City", "Azienda trasporti"]

@st.cache_resource
def load_groq(api_key: str):
    if not api_key: return None
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=api_key)

@st.cache_resource
def load_retriever():
    try: return Retriever()
    except Exception: return None

@st.cache_resource
def load_parametrizer(): return Parametrizer()

@st.cache_resource
def load_classifier(): return IntentClassifier()

@st.cache_resource
def load_prompt_builder(): return PromptBuilder()

def get_deal_from_session() -> dict:
    return {
        "cliente":    st.session_state.get("f_cliente", ""),
        "segmento":   st.session_state.get("f_segmento", ""),
        "budget":     st.session_state.get("f_budget", "")
    }

def format_budget(val: str) -> str:
    try: return f"€ {int(val):,}".replace(",", ".")
    except Exception: return val

def retrieve_context(query: str, retriever) -> tuple[str, list]:
    if retriever is None or not query.strip(): return "", []
    try:
        results = retriever.search(query, top_k=TOP_K)
        parts, sources = [], []
        for r in results:
            text = r.get("text", "").strip()
            fname = r.get("file_name", "fonte sconosciuta")
            if not text: continue
            if fname not in sources: sources.append(fname)
            parts.append(f"[{fname}]\n{text}")
        return "\n\n---\n\n".join(parts), sources
    except Exception: return "", []


def call_llm(llm, system: str, user: str, history: list = None) -> str:
    if llm is None: return "API key Groq non configurata."
    try:
        messages = [SystemMessage(content=system)]

        # Aggiungiamo la memoria conversazionale (limitata agli ultimi 6 messaggi per non saturare i token)
        if history:
            for msg in history[-6:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Aggiungiamo il prompt attuale (che contiene la nuova domanda, il RAG e il contesto)
        messages.append(HumanMessage(content=user))

        return llm.invoke(messages).content
    except Exception as e:
        return f"Errore: {str(e)}"

# ════════════════════════════════════════════════════════════════════════════
# STYLING — INTERFACCIA PROFESSIONALE DARK/SOFT COMPATTA
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Sales Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

GLOBAL_CSS = """
<style>
/* Sfondo scuro riposante per l'applicazione principale */
.stApp {
    background-color: #1e1e24 !important;
    color: #f4f5f7 !important;
}

/* Stile Sidebar Fissa, più scura e compatta */
[data-testid="stSidebar"] {
    background-color: #141419 !important;
    border-right: 1px solid #2d2d38 !important;
}

/* Riduzione degli spazi interni della sidebar per un look più denso e ordinato */
[data-testid="stSidebarUserContent"] {
    padding-top: 1.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 11.5px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #a0aec0 !important;
    border-bottom: 1px solid #2d2d38;
    padding-bottom: 6px;
    margin-bottom: 15px;
}

/* Compattazione spaziatura widget in sidebar */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    margin-bottom: -2px !important;
}

/* Elementi di input della sidebar adattati */
[data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
    background-color: #25252e !important;
    color: #f4f5f7 !important;
    border: 1px solid #3a3a4a !important;
}

/* Contenitori dei report strutturati flat ed eleganti */
.output-container {
    background: #25252e;
    border: 1px solid #3a3a4a;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.output-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #cbd5e0;
    margin-bottom: 0.4rem;
}
.output-body {
    font-size: 13.5px;
    color: #e2e8f0;
    line-height: 1.6;
}

/* Fix estetici per titoli */
h1, h2, h3, p { color: #f4f5f7 !important; }
.stCaption { color: #718096 !important; }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Caricamento istanze core
llm = load_groq(GROQ_API_KEY)
retriever = load_retriever()
param = load_parametrizer()
classifier = load_classifier()
prompt_builder = load_prompt_builder()

# Inizializzazione Session State
defaults = {
    "f_cliente": "",
    "f_segmento": "",
    "f_budget": "",
    "sel_prodotti": [],
    "analysis_result": None,
    "chat_messages": []
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR COMPATTA — SPECIFICHE AGGIUNTIVE (NON OBBLIGATORIE)
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 📋 Specifiche Aggiuntive")

    st.session_state.f_cliente = st.text_input(
        "Cliente / Ente", value=st.session_state.f_cliente, placeholder="Opzionale (es. Comune di Roma)"
    )
    st.session_state.f_segmento = st.selectbox(
        "Segmento", SEGMENTI, index=SEGMENTI.index(st.session_state.f_segmento) if st.session_state.f_segmento in SEGMENTI else 0
    )

    st.markdown("<label style='font-size:13px; color:#cbd5e0;'>Prodotti di interesse</label>", unsafe_allow_html=True)
    st.session_state.sel_prodotti = st.multiselect(
        "Prodotti", PRODOTTI_OPTIONS, default=st.session_state.sel_prodotti, label_visibility="collapsed"
    )

    st.session_state.f_budget = st.text_input(
        "Budget indicativo (€)", value=st.session_state.f_budget, placeholder="Opzionale"
    )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_analysis = st.button("⚡ Analizza", use_container_width=True, type="primary")
    with col_btn2:
        if st.button("🗑️ Reset", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

# Generazione report strutturato (Le specifiche non sono più obbligatorie per l'esecuzione)
if run_analysis:
    with st.spinner("Generazione quadro di sintesi..."):
        deal = get_deal_from_session()
        rag_query = prompt_builder.build_rag_query(deal)
        rag_context, sources = retrieve_context(rag_query, retriever)
        system_prompt = prompt_builder.get_system_prompt()

        st.session_state.analysis_result = {
            "configurazione": call_llm(llm, system_prompt, prompt_builder.section_prompt("configurazione", deal, rag_context)),
            "normativa": call_llm(llm, system_prompt, prompt_builder.section_prompt("normativa", deal, rag_context)),
            "rischi": call_llm(llm, system_prompt, prompt_builder.section_prompt("rischi", deal, rag_context)),
            "sources": sources
        }

# ════════════════════════════════════════════════════════════════════════════
# AREA CENTRALE — SPAZIO DI LAVORO COMMERCIALE
# ════════════════════════════════════════════════════════════════════════════

st.title("🤖 AI Sales Assistant")
st.caption("Engine SpA · Supporto decisionale e assistente commerciale intelligente")

# Quadro di Sintesi Strutturato (Se generato)
if st.session_state.analysis_result:
    with st.expander("📊 Quadro di Sintesi Strutturato Corrente", expanded=False):
        res = st.session_state.analysis_result

        st.markdown(f'<div class="output-container" style="border-left: 3px solid #1D9E75;"><div class="output-title">⚙️ Configurazione Tecnica</div><div class="output-body">{res["configurazione"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="output-container" style="border-left: 3px solid #378ADD;"><div class="output-title">⚖️ Analisi Normativa</div><div class="output-body">{res["normativa"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="output-container" style="border-left: 3px solid #E24B4A;"><div class="output-title">🔴 Matrice Rischi</div><div class="output-body">{res["rischi"]}</div></div>', unsafe_allow_html=True)

        if res["sources"]:
            st.caption(f"Fonti documentali integrate: {', '.join(res['sources'])}")

st.markdown("---")

# 📄 CONTENITORE CRONOLOGIA CHAT
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_messages:
        st.markdown(
            """
            <div style="text-align: center; color: #718096; padding: 4rem 1rem;">
                <p style="font-size: 22px; margin-bottom: 5px;">💬 Workspace Conversazionale Attivo</p>
                <p style="font-size: 13.5px;">Chiedi bozze di offerta, analisi obiezioni o specifiche tecniche liberamente o usando i filtri opzionali a sinistra.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# 📥 INPUT FISSO IN BASSO
chat_input = st.chat_input("Fai una domanda o richiedi un'action commerciale...")

if chat_input:
    # 1. Inserisci immediatamente il messaggio dell'utente in coda alla lista
    st.session_state.chat_messages.append({"role": "user", "content": chat_input})

    # Forza il rendering immediato del messaggio dell'utente nell'area chat
    with chat_container:
        with st.chat_message("user"):
            st.markdown(chat_input)

    # 2. Mostra uno spinner di caricamento pulito sotto l'ultimo messaggio per la risposta pendente
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Elaborazione risposta commerciale in corso..."):

                # Raccolta contesti RAG + Campi
                deal = get_deal_from_session()
                ctx_text = prompt_builder.deal_to_text(deal)
                rag_ctx, _ = retrieve_context(chat_input, retriever)

                conversational_prompt = f"""
CONTESTO ATTUALE DEL DEAL:
{ctx_text}

DOCUMENTAZIONE DI SUPPORTO INTERNA (RAG):
{rag_ctx if rag_ctx else 'Nessun documento rilevante estratto.'}

RICHIESTA COMMERCIALE UTENTE:
{chat_input}
"""
                # Chiamata Groq con memoria conversazionale
                answer = call_llm(
                    llm,
                    prompt_builder.get_system_prompt(),
                    conversational_prompt,
                    history=st.session_state.chat_messages[:-1]  # Escludiamo l'ultimo messaggio inserito in UI
                )
                st.markdown(answer)

    # 3. Salva la risposta dell'assistente nello stato e rinfresca in modo sincrono
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.rerun()