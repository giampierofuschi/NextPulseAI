import os
import json
from langchain_text_splitters import MarkdownHeaderTextSplitter

# ==========================================
# 1. CONFIGURAZIONE CARTELLE
# ==========================================
cartella_input = "Markdown_Puliti"
cartella_output = "Markdown_Frammentati"

if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)

# ==========================================
# 2. CONFIGURAZIONE DEL MOTORE DI TAGLIO
# ==========================================
# Diciamo al sistema quali simboli Markdown usare come "forbici"
# e come chiamare le etichette (metadati) che genererà.
intestazioni_da_tagliare = [
    ("#", "Titolo_Principale"),   # Es. # DECRETO LEGISLATIVO
    ("##", "Sezione"),            # Es. ## Titolo II
    ("###", "Articolo")           # Es. ### Art. 142
]

separatore_md = MarkdownHeaderTextSplitter(headers_to_split_on=intestazioni_da_tagliare)

# ==========================================
# 3. ESECUZIONE DEL CHUNKING
# ==========================================
print("Avvio il Chunking Semantico basato su Markdown...")
file_processati = 0
totale_chunks = 0

for nome_file in os.listdir(cartella_input):
    if nome_file.endswith(".md"):
        percorso_input = os.path.join(cartella_input, nome_file)
        nome_file_json = nome_file.replace(".md", ".json")
        percorso_output = os.path.join(cartella_output, nome_file_json)
        
        try:
            # 1. Legge il file Markdown pulito
            with open(percorso_input, 'r', encoding='utf-8') as f:
                testo_md = f.read()
                
            # 2. Esegue il taglio automatico
            # Restituisce una lista di oggetti "Document"
            frammenti = separatore_md.split_text(testo_md)
            
            # 3. Prepara i dati per il salvataggio in JSON
            lista_chunks_json = []
            for i, frammento in enumerate(frammenti):
                # Ignora frammenti microscopici (es. refusi o righe vuote sfuggite)
                if len(frammento.page_content.strip()) > 50:
                    lista_chunks_json.append({
                        "id_chunk": i + 1,
                        "metadati_gerarchia": frammento.metadata, # Qui finiscono i # Titoli!
                        "testo": frammento.page_content
                    })
            
            struttura_finale = {
                "documento_origine": nome_file,
                "totale_frammenti": len(lista_chunks_json),
                "frammenti": lista_chunks_json
            }
            
            # 4. Salva il risultato
            with open(percorso_output, 'w', encoding='utf-8') as f:
                json.dump(struttura_finale, f, ensure_ascii=False, indent=4)
                
            print(f"✂️ {nome_file} -> {len(lista_chunks_json)} frammenti generati.")
            file_processati += 1
            totale_chunks += len(lista_chunks_json)
            
        except Exception as e:
            print(f"❌ Errore in {nome_file}: {e}")

print(f"\n*** CHUNKING COMPLETATO CON SUCCESSO! ***")
print(f"File elaborati: {file_processati}")
print(f"Totale frammenti logici pronti per l'AI: {totale_chunks}")