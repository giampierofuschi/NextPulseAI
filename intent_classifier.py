"""
intent_classifier.py — Classificatore di intento
AI Sales Assistant · Engine SpA

Capisce cosa vuole il venditore prima di rispondere,
così il sistema adatta il tipo di risposta.
"""


class IntentClassifier:
    """
    Classifica l'intento di un messaggio in una delle 5 categorie
    rilevanti per il processo commerciale di Engine SpA.

    Usato per:
    - mostrare un badge in UI ("sta chiedendo una configurazione")
    - passare l'intento al system prompt così il LLM struttura la risposta
    - filtrare i chunk RAG per tipo di documento (futuro)
    """

    INTENTS = {

        "normativa": {
            "keywords": [
                "normativa", "norma", "decreto", "omologazione", "omologato",
                "art.", "articolo", "codice della strada", "cds", "mit",
                "ministeriale", "circolare", "direttiva", "gdpr", "anac",
                "approvazione", "autorizzazione", "conforme", "conformità",
                "requisito legale", "obbligatorio per legge", "sanzione",
                "multa", "verbale", "accertamento",
            ],
            "label": "Normativa e compliance",
            "emoji": "⚖️",
            "color": "blue",
            "description": "Il venditore ha bisogno di un riferimento normativo o legale.",
        },

        "configurazione": {
            "keywords": [
                "configura", "configurazione", "quanti varchi", "varchi",
                "soluzione", "offerta", "proposta", "dimensionamento",
                "architettura", "installazione", "setup", "sistema",
                "integrazione", "bidirezionale", "monodirezione",
                "telecamera", "sensore", "hardware", "software",
                "backoffice", "centrale operativa", "postazione",
                "quanti dispositivi", "come funziona", "specifiche tecniche",
            ],
            "label": "Configurazione tecnica",
            "emoji": "⚙️",
            "color": "green",
            "description": "Il venditore sta configurando una soluzione per un cliente.",
        },

        "tender": {
            "keywords": [
                "gara", "appalto", "bando", "capitolato", "requisiti gara",
                "procedura", "aggiudicazione", "offerta tecnica",
                "offerta economica", "punteggio", "criteri", "commissione",
                "stazione appaltante", "codice appalti", "d.lgs 36",
                "mepa", "consip", "ribasso", "base d'asta",
            ],
            "label": "Gara d'appalto",
            "emoji": "📋",
            "color": "orange",
            "description": "Il venditore sta preparando o analizzando una gara.",
        },

        "sales_coaching": {
            "keywords": [
                "competitor", "concorrente", "confronto", "alternativa",
                "perché voi", "perché engine", "costa meno", "prezzo",
                "sconto", "obiezione", "convincere", "vantaggio",
                "differenza", "meglio di", "rispetto a", "vs",
                "argomento", "come rispondo", "cliente dice",
                "non sono convinto", "hanno detto che",
            ],
            "label": "Sales coaching",
            "emoji": "🎯",
            "color": "red",
            "description": "Il venditore ha bisogno di supporto su strategia o obiezioni.",
        },

        "deal_context": {
            "keywords": [
                "comune di", "provincia di", "città di", "cliente",
                "prospect", "incontro", "appuntamento", "visita",
                "call", "riunione", "stakeholder", "assessore",
                "polizia locale", "dirigente", "responsabile",
                "budget", "euro", "finanziamento", "fondi",
                "tempistica", "scadenza", "entro", "mesi",
            ],
            "label": "Contesto deal",
            "emoji": "🏢",
            "color": "violet",
            "description": "Il venditore sta fornendo informazioni su un prospect specifico.",
        },
    }

    DEFAULT_INTENT = {
        "key": "generale",
        "label": "Domanda generale",
        "emoji": "💬",
        "color": "gray",
        "description": "Domanda generica sull'assistente o sui prodotti.",
    }

    def classify(self, text: str) -> dict:
        """
        Classifica il testo e restituisce l'intento con il punteggio più alto.

        Returns:
            {
                "key":         "configurazione",
                "label":       "Configurazione tecnica",
                "emoji":       "⚙️",
                "color":       "green",
                "description": "...",
                "score":       3,        # numero di keyword trovate
                "matches":     ["varchi", "soluzione", "offerta"]
            }
        """
        text_lower = text.lower()
        best_key   = None
        best_score = 0
        best_matches = []

        for intent_key, intent_data in self.INTENTS.items():
            matches = [
                kw for kw in intent_data["keywords"]
                if kw in text_lower
            ]
            score = len(matches)
            if score > best_score:
                best_score   = score
                best_key     = intent_key
                best_matches = matches

        if best_key is None or best_score == 0:
            result = dict(self.DEFAULT_INTENT)
            result["score"]   = 0
            result["matches"] = []
            return result

        result = {
            "key":         best_key,
            "label":       self.INTENTS[best_key]["label"],
            "emoji":       self.INTENTS[best_key]["emoji"],
            "color":       self.INTENTS[best_key]["color"],
            "description": self.INTENTS[best_key]["description"],
            "score":       best_score,
            "matches":     best_matches,
        }
        return result

    def get_response_instructions(self, intent_key: str) -> str:
        """
        Restituisce le istruzioni di formato da iniettare nel prompt
        in base all'intento classificato.
        Il LLM riceve istruzioni specifiche su come strutturare la risposta.
        """
        instructions = {

            "normativa": """
Stai rispondendo a una domanda normativa o di compliance.
Struttura la risposta ESATTAMENTE così:

## Riferimento normativo
[indica la norma, il decreto o l'articolo applicabile — solo se presente nei documenti]

## Cosa dice la norma
[spiega il contenuto in modo chiaro e operativo]

## Implicazioni pratiche per Engine SpA
[cosa significa concretamente per il cliente o per l'installazione]

## Fonte
[nome esatto del documento da cui hai tratto l'informazione]

⚠️ Se l'informazione non è nei documenti forniti, scrivi: "Non ho questo dato nei documenti correnti — verificherò con il team Product."
""",

            "configurazione": """
Stai rispondendo a una richiesta di configurazione tecnica.
Struttura la risposta ESATTAMENTE così:

## Soluzione consigliata
[descrizione della configurazione raccomandata in 2-3 righe]

## Componenti necessari
[lista dei prodotti/moduli Engine SpA necessari]

## Requisiti normativi applicabili
[normativa rilevante per questa configurazione — solo se nei documenti]

## Domande di qualificazione
[2-3 domande che mancano per completare la configurazione, es. "Quanti varchi?", "Serve il controllo bidirezionale?"]

## Attenzione
[eventuali vincoli, rischi o prerequisiti da considerare]
""",

            "tender": """
Stai supportando la preparazione di una risposta a una gara d'appalto.
Struttura la risposta ESATTAMENTE così:

## Analisi della gara
[cosa sappiamo della gara dal contesto fornito]

## Requisiti normativi chiave
[normativa rilevante per questa tipologia di gara]

## Punti di forza Engine SpA per questa gara
[argomenti tecnici e commerciali da valorizzare]

## Rischi e attenzioni
[elementi critici da presidiare nell'offerta]

## Prossimi passi
[azioni concrete consigliate per il team]
""",

            "sales_coaching": """
Stai supportando il venditore su una strategia commerciale o un'obiezione.
Struttura la risposta ESATTAMENTE così:

## L'obiezione / la situazione
[riformula brevemente il problema commerciale]

## Argomenti chiave
[3-4 punti concreti per rispondere o posizionarsi]

## Come dirlo al cliente
[frase o script pronto da usare nella conversazione]

## Da non dire
[errori comuni da evitare in questa situazione]
""",

            "deal_context": """
Il venditore ti sta fornendo informazioni su un prospect.
Struttura la risposta ESATTAMENTE così:

## Riepilogo deal
[riepiloga i dati chiave del prospect che hai capito]

## Valutazione preliminare
[potenziale fit con i prodotti Engine SpA]

## Informazioni mancanti
[cosa serve sapere ancora per qualificare bene il deal]

## Raccomandazione
[prossimo passo commerciale consigliato]
""",

            "generale": """
Rispondi in modo professionale e conciso.
Se puoi, cita la fonte del documento tra parentesi per ogni dato tecnico.
Se non hai l'informazione nei documenti, dillo esplicitamente.
""",
        }

        return instructions.get(intent_key, instructions["generale"])


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":

    classifier = IntentClassifier()

    test_cases = [
        "Qual è la normativa per installare un autovelox su una strada provinciale?",
        "Devo configurare una soluzione ZTL per un comune con 3 varchi",
        "Stiamo partecipando a una gara d'appalto del Comune di Milano da 500k",
        "Il cliente dice che il competitor costa il 30% in meno, come rispondo?",
        "Ho un incontro con il Comune di Brescia, budget 400k, vogliono speed cam",
        "Come posso resettare la chat?",
    ]

    print("=" * 56)
    print("  Test IntentClassifier")
    print("=" * 56)

    for text in test_cases:
        result = classifier.classify(text)
        print(f"\n📝 \"{text[:60]}\"")
        print(f"   → {result['emoji']} {result['label']} (score: {result['score']})")
        if result["matches"]:
            print(f"   keyword: {result['matches']}")
