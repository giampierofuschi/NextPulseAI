# S.P.E.E.D. 🚦
### Smart Pre-sales Engine for Enforcement Data

AI-powered sales assistant for the traffic enforcement domain, developed by Team "Dodici" during **Next Pulse**, a hackathon organized by **Zenita Group** (06-07/06/2026, Chieti).

---

## 📌 Il Problema

Il team commerciale di Engine SpA deve raccogliere e incrociare informazioni sparse — documentazione tecnica, offerte passate, requisiti di gara, vincoli normativi, configurazioni su misura — tutto con tempi di risposta strettissimi. Ogni minuto di ricerca è una trattativa che rallenta.

## 💡 La Soluzione

S.P.E.E.D. è un copilota virtuale progettato per affiancare il team commerciale. Il venditore formula una domanda in linguaggio naturale, il sistema incrocia i cataloghi prodotti con le normative vigenti e genera risposte pronte per essere inserite direttamente nella proposta commerciale.

Utilizza la tecnologia **RAG (Retrieval Augmented Generation)** basandosi esclusivamente su documenti ufficiali:
- **Dati pubblici** — normative e decreti ministeriali
- **Dati riservati** — listino prezzi Engine SpA
- **Esperienze pregresse** — storico vendite

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — interfaccia utente
- [LangChain](https://www.langchain.com/) — orchestrazione LLM
- [Groq](https://groq.com/) — inference LLM
- [FAISS](https://github.com/facebookresearch/faiss) — vector store per la knowledge base

## 🚀 Come avviare il progetto

### 1. Clona la repository

```bash
git clone https://github.com/giampierofuschi/NextPulseAI.git
cd NextPulseAI
```

### 2. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configura la API Key

Crea un file `.env` nella root del progetto con il seguente contenuto:
> ⚠️ La API key non è inclusa nella repository per motivi di sicurezza. Puoi ottenere una chiave gratuita su [console.groq.com](https://console.groq.com).

### 4. Avvia l'applicazione

```bash
streamlit run main.py
```

## 👥 Il Team "Dodici"

| Nome | Ruolo |
|------|-------|
| Caterina Carli | CEO & Fondatrice — Responsabile della presentazione e del coordinamento del team |
| Giampiero Fuschi | DEV — Frontend & Backend Developer, progettista interfacce e sviluppo core |
| Alessandro Caruso | DEV — Backend & Frontend Engineer, sviluppa il motore software e l'interfaccia utente |
| Daniele Amato | COO — Data sourcing, roadmap e supporto alla presentazione finale |
| Andrei Rosca | DEV — AI & Data Specialist, si occupa di parametrizzazione, indicizzazione e data cleaning |

## 🗺️ Roadmap

- [x] Controllo manuale della documentazione
- [ ] Controllo automatico della documentazione
- [ ] Generalizzazione del modello a legislazioni estere
- [ ] Espansione del modello ad altri contesti
