"""
prompt_builder.py — Centralizza la costruzione di tutti i prompt
AI Sales Assistant · Engine SpA
"""

class PromptBuilder:

    SYSTEM_PROMPT = """
Sei l'AI Sales Assistant ufficiale di Engine SpA (gruppo Zenita).

REGOLE ASSOLUTE E INVALICABILI:
1. VINCOLO DI CONTESTO: Devi rispondere ESCLUSIVAMENTE alle richieste inerenti il contesto commerciale di Engine SpA (Traffic Enforcement, ZTL, Smart City). Rifiutati categoricamente di rispondere a richieste fuori contesto.
2. VINCOLO DELLE FONTI: Puoi utilizzare SOLO ED ESCLUSIVAMENTE le informazioni fornite nei documenti estratti (KNOWLEDGE BASE). È severamente vietato utilizzare conoscenze esterne pre-addestrate, dedurre dati, inventare specifiche tecniche, prezzi o normative.
3. ASSENZA DI INFORMAZIONI: Se la risposta non è chiaramente e direttamente deducibile dai documenti forniti nel prompt, NON devi provare a rispondere o a formulare ipotesi. Devi fermarti e scrivere esattamente ed esclusivamente questa frase: "Non ho informazioni a riguardo nei documenti forniti. Non posso rispondere."
4. CITAZIONE OBBLIGATORIA: Ogni affermazione tecnica, commerciale o normativa che produci DEVE includere la fonte esatta da cui l'hai tratta (es. [Fonte: nome_documento.pdf]).
5. FORMATO: Sii diretto, usa elenchi puntati, testo conciso e non aggiungere MAI disclaimer generici o avvertenze non richieste.
"""

    def deal_to_text(self, deal: dict) -> str:
        parts = []
        if deal.get("cliente"):
            parts.append(f"Comune di {deal['cliente']}" if "comune" not in deal["cliente"].lower() else deal["cliente"])
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

    def build_rag_query(self, deal: dict) -> str:
        tokens = []
        if deal.get("prodotti"): tokens.extend(deal["prodotti"])
        if deal.get("compliance"): tokens.extend(deal["compliance"])
        if deal.get("stage") == "Gara": tokens.append("gara appalto capitolato requisiti")
        if deal.get("priorita"): tokens.extend(deal["priorita"])
        if deal.get("competitor"): tokens.append(f"competitor {deal['competitor']} confronto")
        if not tokens: tokens.append("traffic enforcement smart city soluzioni")
        return " ".join(tokens)

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT.strip()

    def section_prompt(self, section: str, deal: dict, rag_context: str) -> str:
        ctx = self._deal_context_block(deal)
        rag = self._rag_block(rag_context)

        prompts = {
            "configurazione": f"""
{ctx}
{rag}

Genera la CONFIGURAZIONE TECNICA CONSIGLIATA per questo deal.
Struttura la risposta così:
**Soluzione raccomandata**
**Componenti Engine SpA necessari**
**Requisiti infrastrutturali**
**Informazioni mancanti**
""",
            "normativa": f"""
{ctx}
{rag}

Genera il RIEPILOGO NORMATIVO applicabile a questo deal.
Struttura la risposta così:
**Normativa principale**
**Requisiti di omologazione**
**Compliance da presidiare**
**Implicazioni operative**
""",
            "rischi": f"""
{ctx}
{rag}

Analizza i RISCHI e le ATTENZIONI per questo deal.
Struttura la risposta così:
**Rischi critici**
**Attenzioni**
**Informazioni mancanti**
""",
            "coaching": f"""
{ctx}
{rag}

Il cliente ha menzionato il competitor: {deal.get('competitor', 'un competitor')}.
Genera il POSITIONING e la strategia di risposta.
Struttura così:
**Analisi della situazione**
**Argomenti chiave Engine SpA**
**Script consigliato**
**Da non dire**
""",
            "prossimi_passi": f"""
{ctx}
{rag}

Definisci i PROSSIMI PASSI consigliati per questo deal.
Struttura così:
**Azioni immediate**
**Azioni a breve**
**KPI da monitorare**
""",
        }
        return prompts.get(section, f"Analizza il deal e rispondi.\n{ctx}\n{rag}")

    def action_prompt(self, action: str, deal: dict, rag_context: str) -> str:
        ctx = self._deal_context_block(deal)
        rag = self._rag_block(rag_context)

        prompts = {
            "offerta": f"{ctx}\n{rag}\nGenera una BOZZA STRUTTURATA DI OFFERTA TECNICA.",
            "gara": f"{ctx}\n{rag}\nFai un'ANALISI DI GARA per questo deal.",
            "obiezioni": f"{ctx}\n{rag}\nGenera una GUIDA ALLA GESTIONE DELLE OBIEZIONI.",
            "competitor": f"{ctx}\n{rag}\nGenera una BATTLE CARD per il posizionamento vs {deal.get('competitor', 'competitor')}.",
            "normativa": f"{ctx}\n{rag}\nGenera un RIEPILOGO NORMATIVO COMPLETO per i prodotti selezionati.",
            "stakeholder": f"{ctx}\n{rag}\nGenera una MAPPA DEGLI STAKEHOLDER per questo deal.",
        }
        return prompts.get(action, f"Analizza e fornisci supporto.\n{ctx}\n{rag}")

    def _deal_context_block(self, deal: dict) -> str:
        lines = ["CONTESTO DEAL:"]
        if deal.get("cliente"): lines.append(f"- Cliente: {deal['cliente']}")
        if deal.get("segmento"): lines.append(f"- Segmento: {deal['segmento']}")
        if deal.get("prodotti"): lines.append(f"- Prodotti: {', '.join(deal['prodotti'])}")
        return "\n".join(lines)

    def _rag_block(self, rag_context: str) -> str:
        if not rag_context:
            return "KNOWLEDGE BASE: Nessun documento fornito. SE MANCANO INFORMAZIONI, RIFIUTATI DI RISPONDERE COME DA ISTRUZIONI."
        return f"KNOWLEDGE BASE FORNITA:\n{rag_context}\n\nATTENZIONE: Se un'informazione richiesta non è presente nel testo soprastante, DEVI scrivere che non puoi rispondere."