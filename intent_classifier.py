"""
intent_classifier.py — Classificatore di intento
AI Sales Assistant · Engine SpA
"""

class IntentClassifier:

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
        text_lower = text.lower()
        best_key   = None
        best_score = 0
        best_matches = []

        for intent_key, intent_data in self.INTENTS.items():
            matches = [kw for kw in intent_data["keywords"] if kw in text_lower]
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

        return {
            "key":         best_key,
            "label":       self.INTENTS[best_key]["label"],
            "emoji":       self.INTENTS[best_key]["emoji"],
            "color":       self.INTENTS[best_key]["color"],
            "description": self.INTENTS[best_key]["description"],
            "score":       best_score,
            "matches":     best_matches,
        }