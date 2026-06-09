# Engine SpA — AI Sales Assistant · Deal Cockpit

AI Sales Assistant per il team commerciale di Engine SpA (gruppo Zenita).
Interfaccia strutturata a pannelli per supportare trattative di Traffic Enforcement.

---

## Struttura del progetto

```
engine_sales_assistant/
│
├── main.py               ← App Streamlit — Deal Cockpit (punto di ingresso)
├── prompt_builder.py     ← Costruzione di tutti i prompt per sezione/azione
├── parametrizer.py       ← Estrazione parametrica da testo (keyword + regex)
├── intent_classifier.py  ← Classificazione intento del deal
├── retriever.py          ← Ricerca vettoriale FAISS
├── index_builder.py      ← Costruzione dell'indice FAISS
├── index.py              ← Script di avvio indicizzazione
├── requirements.txt      ← Dipendenze Python
│
├── knowledge/            ← [DA CREARE] cartella con i documenti Engine SpA
│   ├── normativa/
│   ├── prodotti/
│   └── casi_cliente/
│
└── storage_index/        ← [GENERATO AUTOMATICAMENTE] indice FAISS + metadata
    ├── faiss.index
    └── metadata.pkl
```

---

## Setup e avvio

### 1. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configura la API Key di Groq

Crea un file `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Oppure esporta la variabile d'ambiente:

```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Carica i documenti nella knowledge base

Crea la cartella `knowledge/` e inserisci i file tecnici (PDF, DOCX, TXT):

```
knowledge/
├── Quadro_normativo_autovelox.pdf
├── Scheda_tecnica_SpeedCam.pdf
├── FAQ_prodotti_Engine.pdf
└── ...
```

### 4. Costruisci l'indice vettoriale

```bash
python index.py
```

Questo genera la cartella `storage_index/` con l'indice FAISS.
Va eseguito una sola volta (o ogni volta che aggiungi nuovi documenti).

### 5. Avvia l'app

```bash
streamlit run main.py
```

---

## Architettura

```
Form strutturato (Deal Briefing)
        │
        ▼
PromptBuilder.build_rag_query()
        │
        ▼
Retriever (FAISS) ──── storage_index/
        │
        ▼
Parametrizer + IntentClassifier
        │
        ▼
PromptBuilder.section_prompt() × 5 sezioni
        │
        ▼
Groq LLM (llama-3.3-70b-versatile)
        │
        ▼
Deal Cockpit UI — 5 pannelli strutturati
```

---

## Interfaccia — Deal Cockpit

| Pannello | Contenuto |
|---|---|
| Sinistra | Form di qualificazione deal (cliente, stage, prodotti, compliance...) |
| Centro | Output AI strutturato: configurazione, normativa, rischi, coaching, prossimi passi |
| Destra | Quick Actions (bozza offerta, analisi gara, obiezioni, competitor...) + stato deal |
| Basso | Chat conversazionale (secondaria, collassabile) |

---

## Quick Actions disponibili

- **Genera bozza offerta** — struttura completa offerta tecnica
- **Analisi capitolato gara** — checklist e rischi per gare pubbliche
- **Gestione obiezioni** — guide e script per le obiezioni tipiche
- **Positioning vs competitor** — battle card con script pronto
- **Riferimenti normativi** — riepilogo completo normativa applicabile
- **Mappa stakeholder** — chi coinvolgere e come per fase e segmento

---

## Note tecniche

- **Modello LLM**: `llama-3.3-70b-versatile` via Groq API
- **Embedding**: `all-MiniLM-L6-v2` via sentence-transformers
- **Vector store**: FAISS IndexFlatL2 (distanza L2 — score più basso = più rilevante)
- **Chunk size**: 1000 token, overlap 200
- **RAG top-k**: 5 chunk per query

---

## Nota sui dati

I dataset e i materiali forniti potrebbero contenere dati sintetici o modificati
per motivi di riservatezza aziendale (come indicato nel brief Zenita).
Il sistema è progettato per:
- Citare sempre la fonte documentale
- Segnalare esplicitamente quando un'informazione non è nei documenti
- Non inventare mai normative, prezzi o specifiche tecniche
