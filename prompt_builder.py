"""
prompt_builder.py — Centralizza la costruzione di tutti i prompt
AI Sales Assistant · Engine SpA · Deal Cockpit

Separato da main.py per mantenere la logica testabile e modificabile
senza toccare l'interfaccia.
"""


class PromptBuilder:
    """
    Costruisce system prompt, prompt per sezione e prompt per azioni rapide.
    Riceve sempre un dict 'deal' con le chiavi standard del form.
    """

    SYSTEM_PROMPT = """
Sei l'AI Sales Assistant ufficiale di Engine SpA (gruppo Zenita),
leader nel Traffic Enforcement e nelle soluzioni Smart City italiane.

Il tuo compito è supportare il team commerciale e pre-sales nella
preparazione di offerte, configurazione soluzioni e risposta a gare.

REGOLE ASSOLUTE:
1. Rispondi SOLO su: controllo velocità, ZTL, semaforo rosso, analytics mobilità urbana.
2. Non inventare mai normative, omologazioni, prezzi o specifiche tecniche.
   Se un dato non è nei documenti forniti, scrivi esattamente:
   "Non ho questo dato nei documenti correnti — da verificare con il team Product."
3. Ogni dato tecnico o normativo citato deve essere seguito dal nome del file fonte
   tra parentesi. Es: (Fonte: Quadro_normativo_autovelox.docx)
4. Rispondi in italiano, in modo professionale e operativo.
5. Usa elenchi puntati per le liste, testo breve e diretto.
6. Non aggiungere mai disclaimer generici o avvertenze legali non richieste.
7. Se mancano dati chiave per rispondere, segnala esattamente quali mancano.
"""

    # ─────────────────────────────────────────────
    # DEAL → TESTO (per parametrizer e classifier)
    # ─────────────────────────────────────────────

    def deal_to_text(self, deal: dict) -> str:
        """
        Converte il deal strutturato in testo naturale
        per Parametrizer e IntentClassifier.
        """
        parts = []

        if deal.get("cliente"):
            parts.append(f"Comune di {deal['cliente']}" if "comune" not in deal["cliente"].lower()
                         else deal["cliente"])
        if deal.get("segmento"):
            parts.append(f"Segmento: {deal['segmento']}.")
        if deal.get("stage"):
            parts.append(f"Fase commerciale: {deal['stage']}.")
            if deal["stage"] == "Gara":
                parts.append("Stiamo partecipando a una gara d'appalto.")
        if deal.get("prodotti"):
            parts.append(f"Interesse per: {', '.join(deal['prodotti'])}.")
        if deal.get("priorita"):
            parts.append(f"Priorità cliente: {', '.join(deal['priorita'])}.")
        if deal.get("budget"):
            parts.append(f"Budget {deal['budget']} euro.")
        if deal.get("deploy"):
            parts.append(f"Deployment {deal['deploy']}.")
        if deal.get("compliance"):
            parts.append(f"Compliance richiesta: {', '.join(deal['compliance'])}.")
        if deal.get("competitor"):
            parts.append(f"Competitor menzionato: {deal['competitor']}.")
        if deal.get("note"):
            parts.append(deal["note"])

        return " ".join(parts) if parts else "Nuovo deal senza dettagli."

    # ─────────────────────────────────────────────
    # RAG QUERY
    # ─────────────────────────────────────────────

    def build_rag_query(self, deal: dict) -> str:
        """
        Costruisce la query ottimizzata per la ricerca vettoriale.
        Più specifica del testo libero per migliorare il retrieval.
        """
        tokens = []

        if deal.get("prodotti"):
            tokens.extend(deal["prodotti"])
        if deal.get("compliance"):
            tokens.extend(deal["compliance"])
        if deal.get("stage") == "Gara":
            tokens.append("gara appalto capitolato requisiti")
        if deal.get("priorita"):
            tokens.extend(deal["priorita"])
        if deal.get("competitor"):
            tokens.append(f"competitor {deal['competitor']} confronto")

        # Fallback generico
        if not tokens:
            tokens.append("traffic enforcement smart city soluzioni")

        return " ".join(tokens)

    # ─────────────────────────────────────────────
    # SYSTEM PROMPT
    # ─────────────────────────────────────────────

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT.strip()

    # ─────────────────────────────────────────────
    # PROMPT PER SEZIONE
    # ─────────────────────────────────────────────

    def section_prompt(self, section: str, deal: dict, rag_context: str) -> str:
        """
        Restituisce il prompt specifico per ogni sezione dell'output.
        """
        ctx = self._deal_context_block(deal)
        rag = self._rag_block(rag_context)

        prompts = {

            "configurazione": f"""
{ctx}
{rag}

Genera la CONFIGURAZIONE TECNICA CONSIGLIATA per questo deal.
Struttura la risposta così:

**Soluzione raccomandata**
[2-3 righe che descrivono la configurazione più adatta]

**Componenti Engine SpA necessari**
[lista prodotti/moduli rilevanti basata sui prodotti selezionati]

**Requisiti infrastrutturali**
[server, connettività, hardware — in base al deployment selezionato]

**Informazioni mancanti per completare il dimensionamento**
[domande specifiche ancora aperte, es. numero varchi, tipo di strada]

Cita la fonte per ogni dato tecnico specifico. Sii diretto e operativo.
""",

            "normativa": f"""
{ctx}
{rag}

Genera il RIEPILOGO NORMATIVO applicabile a questo deal.
Struttura la risposta così:

**Normativa principale**
[norma/decreto più rilevante per i prodotti e la fase indicati]

**Requisiti di omologazione**
[obblighi specifici per i prodotti selezionati]

**Compliance da presidiare**
[GDPR, ANAC, CdS — solo quella rilevante per questo deal]

**Implicazioni operative**
[cosa significa concretamente per il cliente]

Se le informazioni non sono nei documenti, segnalalo esplicitamente.
Cita sempre la fonte normativa tra parentesi.
""",

            "rischi": f"""
{ctx}
{rag}

Analizza i RISCHI e le ATTENZIONI per questo deal.
Struttura la risposta così:

**Rischi critici** (priorità alta)
[blockers che potrebbero far saltare il deal o la gara]

**Attenzioni** (priorità media)
[elementi da monitorare nella trattativa]

**Informazioni mancanti** (da qualificare)
[dati che servono prima di procedere]

Sii specifico e pratico. Usa il contesto del deal per essere pertinente.
""",

            "coaching": f"""
{ctx}
{rag}

Il cliente ha menzionato il competitor: {deal.get('competitor', 'un competitor')}.
Genera il POSITIONING e la strategia di risposta.
Struttura così:

**Analisi della situazione**
[cosa probabilmente sta valutando il cliente]

**Argomenti chiave Engine SpA**
[3-4 punti di differenziazione concreti]

**Script consigliato**
[frase/risposta pronta da usare con il cliente]

**Da non dire**
[errori tipici da evitare in questa situazione]
""",

            "prossimi_passi": f"""
{ctx}
{rag}

Definisci i PROSSIMI PASSI consigliati per questo deal.
Considera la fase commerciale attuale: {deal.get('stage', 'non specificata')}.

Struttura così:

**Azioni immediate** (entro 48h)
[cosa fare subito]

**Azioni a breve** (entro 2 settimane)
[preparazione, documentazione, contatti]

**KPI da monitorare**
[metriche per valutare avanzamento del deal]

Sii operativo. Indica chi deve fare cosa quando possibile.
""",
        }

        return prompts.get(section, f"Analizza il deal e rispondi in modo professionale.\n{ctx}\n{rag}")

    # ─────────────────────────────────────────────
    # PROMPT AZIONI RAPIDE
    # ─────────────────────────────────────────────

    def action_prompt(self, action: str, deal: dict, rag_context: str) -> str:
        """
        Prompt per le Quick Actions della colonna destra.
        """
        ctx = self._deal_context_block(deal)
        rag = self._rag_block(rag_context)

        prompts = {

            "offerta": f"""
{ctx}
{rag}

Genera una BOZZA STRUTTURATA DI OFFERTA TECNICA per questo deal.

Includi:
1. Introduzione e comprensione del problema del cliente
2. Soluzione proposta (prodotti Engine SpA, architettura, deployment)
3. Benefici attesi e valore per il cliente
4. Requisiti normativi e compliance garantita
5. Roadmap di implementazione (macro fasi)
6. Riferimento a casi simili (se presenti nei documenti)

Sii professionale e orientato al valore. Cita le fonti per dati tecnici.
""",

            "gara": f"""
{ctx}
{rag}

Fai un'ANALISI DI GARA per questo deal.

Struttura:

**Analisi del contesto di gara**
[cosa sappiamo della procedura]

**Normativa di riferimento per gare pubbliche**
[D.Lgs 36/2023, codice appalti, ANAC]

**Punti di forza Engine SpA per questa gara**
[argomenti tecnici e commerciali da valorizzare nell'offerta]

**Rischi nell'offerta**
[elementi critici da presidiare]

**Documentazione da preparare**
[lista checklist per l'offerta tecnica + economica]

**Prossimi passi**
[azioni concrete per il team]
""",

            "obiezioni": f"""
{ctx}
{rag}

Il cliente ha sollevato obiezioni o sta valutando alternative.
Genera una GUIDA ALLA GESTIONE DELLE OBIEZIONI per questo deal.

Struttura:

**Obiezioni più probabili in questa fase ({deal.get('stage', 'nd')})**
[le 3-4 obiezioni tipiche per segmento {deal.get('segmento', 'nd')}]

**Risposta consigliata per ogni obiezione**
[argomenti, dati, riferimenti da usare]

**Come chiudere la conversazione**
[passo successivo da proporre al cliente dopo aver risposto]
""",

            "competitor": f"""
{ctx}
{rag}

Genera una BATTLE CARD per il posizionamento vs {deal.get('competitor', 'competitor')}.

Struttura:

**Profilo del competitor**
[punti di forza dichiarati dal mercato]

**Dove Engine SpA è superiore**
[differenziatori concreti — tecnici, normativi, di servizio]

**Dove il competitor può essere più forte**
[essere onesti sulle aree di miglioramento]

**Come rispondere se il cliente confronta prezzi**
[argomenti TCO, valore a lungo termine, supporto locale]

**Script di risposta pronto**
[frase da usare quando il cliente menziona il competitor]
""",

            "normativa": f"""
{ctx}
{rag}

Genera un RIEPILOGO NORMATIVO COMPLETO per i prodotti selezionati:
{', '.join(deal.get('prodotti', ['traffic enforcement'])) or 'traffic enforcement'}

Includi:
- Decreto MIT e omologazioni necessarie per ogni prodotto
- Articoli del Codice della Strada applicabili
- Requisiti GDPR per trattamento dati (targhe, immagini)
- Normativa su gare pubbliche (se fase = Gara)
- Direttive europee applicabili (NIS2 se cybersecurity)

Per ogni norma: indica il riferimento esatto e l'implicazione pratica.
Cita la fonte documentale per ogni informazione.
""",

            "stakeholder": f"""
{ctx}
{rag}

Genera una MAPPA DEGLI STAKEHOLDER per questo deal.

Per ogni stakeholder indicato:
- Ruolo e interesse nel progetto
- Livello di influenza sulla decisione
- Preoccupazioni tipiche
- Come coinvolgerlo / messaggio chiave

Stakeholder tipici per {deal.get('segmento', 'ente pubblico')}:
- Decisori (es. Assessore alla Mobilità, Sindaco)
- Tecnici (es. Ufficio IT, Polizia Locale)
- Amministrativi (es. Ufficio Gare, Ragioneria)
- Operativi (es. Mobility Manager)

Fase attuale: {deal.get('stage', 'non specificata')}.
Adatta i consigli alla fase commerciale corrente.
""",
        }

        return prompts.get(action, f"Analizza il deal e fornisci supporto operativo.\n{ctx}\n{rag}")

    # ─────────────────────────────────────────────
    # HELPERS PRIVATI
    # ─────────────────────────────────────────────

    def _deal_context_block(self, deal: dict) -> str:
        lines = ["CONTESTO DEAL:"]
        if deal.get("cliente"):    lines.append(f"- Cliente: {deal['cliente']}")
        if deal.get("segmento"):   lines.append(f"- Segmento: {deal['segmento']}")
        if deal.get("stage"):      lines.append(f"- Fase commerciale: {deal['stage']}")
        if deal.get("budget"):     lines.append(f"- Budget: {deal['budget']} €")
        if deal.get("prodotti"):   lines.append(f"- Prodotti di interesse: {', '.join(deal['prodotti'])}")
        if deal.get("priorita"):   lines.append(f"- Priorità cliente: {', '.join(deal['priorita'])}")
        if deal.get("deploy"):     lines.append(f"- Deployment: {deal['deploy']}")
        if deal.get("compliance"): lines.append(f"- Compliance richiesta: {', '.join(deal['compliance'])}")
        if deal.get("competitor"): lines.append(f"- Competitor menzionato: {deal['competitor']}")
        if deal.get("note"):       lines.append(f"- Note: {deal['note']}")
        return "\n".join(lines)

    def _rag_block(self, rag_context: str) -> str:
        if not rag_context:
            return (
                "KNOWLEDGE BASE: Nessun documento rilevante trovato per questa query. "
                "Rispondi solo con ciò che sai con certezza e segnala i limiti."
            )
        return (
            f"DOCUMENTI DALLA KNOWLEDGE BASE:\n{rag_context}\n\n"
            "Usa esclusivamente questi documenti per dati tecnici e normativi. "
            "Cita il nome del file fonte tra parentesi per ogni dato specifico."
        )
