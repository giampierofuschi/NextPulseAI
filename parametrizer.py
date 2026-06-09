import json
import re


class Parametrizer:

    CUSTOMER_SEGMENTS = {
        "comune": "municipality",
        "polizia locale": "local_police",
        "provincia": "province",
        "gestore autostradale": "highway_operator",
        "smart city": "smart_city",
        "azienda trasporti": "mobility_company",
    }

    USE_CASES = {
        "velocità": "speed_enforcement",
        "ztl": "ztl_control",
        "semaforo rosso": "redlight_enforcement",
        "traffico": "traffic_monitoring",
        "analytics": "mobility_analytics",
        "parcheggi": "smart_parking",
    }

    PRODUCTS = {
        "speed cam": "speed_cam",
        "ocr": "ocr_ztl",
        "ztl": "ocr_ztl",
        "red light": "redlight",
        "backoffice": "backoffice",
        "analytics": "analytics_ai",
        "mobile": "mobile_unit",
    }

    PRIORITIES = {
        "incidenti": "safety",
        "sicurezza": "safety",
        "compliance": "compliance",
        "traffico": "traffic_reduction",
        "costi": "cost_reduction",
        "introiti": "revenue_growth",
    }

    SALES_STAGE = {
        "lead": "lead",
        "discovery": "discovery",
        "demo": "demo",
        "gara": "tender",
        "offerta": "proposal",
        "negoziazione": "negotiation",
    }

    STAKEHOLDERS = {
        "assessore": "mobility_councilor",
        "polizia locale": "local_police",
        "ufficio it": "it_department",
        "gare": "procurement",
        "sindaco": "mayor",
        "mobility manager": "mobility_manager",
    }

    def __init__(self):
        pass


    def match_keywords(self, text: str, mapping: dict):

        text = text.lower()
        results = set()

        for k, v in mapping.items():
            if k in text:
                results.add(v)

        return list(results)


    def extract_budget(self, text: str):

        match = re.search(r"(\d{3,})\s*euro", text.lower())
        return int(match.group(1)) if match else None

    def extract_city(self, text: str):

        match = re.search(r"comune di ([a-zàèéìòù\s]+)", text.lower())
        return match.group(1).strip().title() if match else ""


    def extract_parameters(self, text: str):

        return {
            "city": self.extract_city(text),

            "customer_segment": self.match_keywords(text, self.CUSTOMER_SEGMENTS),
            "use_cases": self.match_keywords(text, self.USE_CASES),
            "products": self.match_keywords(text, self.PRODUCTS),
            "sales_stage": self.match_keywords(text, self.SALES_STAGE),
            "stakeholders": self.match_keywords(text, self.STAKEHOLDERS),

            "budget": self.extract_budget(text),

            "integrations": [],
            "risks": [],
            "missing_fields": [],
            "ambiguities": [],
            "confidence": {}
        }

    def build_query(self, data: dict):

        parts = []

        if data.get("customer_segment"):
            parts.append(f"segment:{data['customer_segment']}")

        if data.get("city"):
            parts.append(f'city:"{data["city"]}"')

        if data.get("sales_stage"):
            parts.append(f"stage:{data['sales_stage']}")

        if data.get("use_cases"):
            parts.append(f"use_cases:[{','.join(data['use_cases'])}]")

        if data.get("products"):
            parts.append(f"products:[{','.join(data['products'])}]")

        if data.get("stakeholders"):
            parts.append(f"stakeholders:[{','.join(data['stakeholders'])}]")

        return " AND ".join(parts)

    def validate(self, data: dict):

        errors = []

        if not data.get("customer_segment"):
            errors.append("customer_segment mancante")

        if not data.get("products"):
            errors.append("products mancanti")

        if not data.get("use_cases"):
            errors.append("use_cases non identificati")

        if not data.get("sales_stage"):
            errors.append("sales_stage non identificato")

        if "tender" in data.get("sales_stage", []):
            if "anac" not in data.get("compliance", []):
                errors.append("tender senza compliance ANAC")

        return errors

    def process(self, text: str):

        extracted = self.extract_parameters(text)
        query = self.build_query(extracted)
        validation = self.validate(extracted)

        return {
            "structured_parameters": extracted,
            "query": query,
            "validation": validation
        }



if __name__ == "__main__":

    extractor = Parametrizer()

    note = """
Incontro con il Comune di Bologna
e la Polizia Locale.

Interesse per sistemi OCR ZTL e analytics traffico.

Priorità: compliance GDPR e riduzione incidenti.

Ufficio IT coinvolto.

Gara prevista entro 2 mesi.

Budget 300000 euro.

Deployment cloud.
"""

    result = extractor.process(note)

    print("\nPARAMETRI ESTRATTI:\n")
    print(json.dumps(result["structured_parameters"], indent=2, ensure_ascii=False))

    print("\nQUERY:\n")
    print(result["query"])

    print("\nVALIDATION:\n")
    for v in result["validation"]:
        print(v)