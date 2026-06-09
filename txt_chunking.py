import os
import re
import json

# ==========================================
# 1. CONFIGURAZIONE CARTELLE
# ==========================================
# Cartella da cui prelevare i testi puliti
cartella_input = "Testi_Puliti"
# Nuova cartella dove salveremo i frammenti in formato JSON
cartella_output = "Testi_Frammentati"

if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)

# ==========================================
# 2. MOTORE DI CHUNKING SEMANTICO
# ==========================================
def dividi_per_articoli(testo):
    # Regex Lookahead: Cerca un ritorno a capo seguito da "Articolo" o "Art." e un numero.
    # Il taglio avviene prima della parola, mantenendola nel frammento.
    pattern = r'\n(?=(?:Articolo|Art\.)\s*\d+)'
    
    # Esegue la divisione
    frammenti_grezzi = re.split(pattern, testo, flags=re.IGNORECASE)
    
    chunks_validi = []
    
    for i, frammento in enumerate(frammenti_grezzi):
        frammento_pulito = frammento.strip()
        
        # Filtro: salviamo solo i frammenti che contengono almeno 50 caratteri.
        # Questo elimina eventuali "rimasugli" vuoti o titoli orfani.
        if len(frammento_pulito) > 50:
            chunks_validi.append({
                "id_chunk": i + 1,
                "testo": frammento_pulito
            })
            
    return chunks_validi

# ==========================================
# 3. ESECUZIONE DEL PROCESSO
# ==========================================
print("Avvio il Chunking Semantico dei documenti...")
file_processati = 0
totale_chunks_generati = 0

for nome_file in os.listdir(cartella_input):
    if nome_file.endswith(".txt"):
        percorso_input = os.path.join(cartella_input, nome_file)
        # Cambiamo l'estensione da .txt a .json
        nome_file_json = nome_file.replace(".txt", ".json")
        percorso_output = os.path.join(cartella_output, nome_file_json)
        
        try:
            # Legge il testo pulito
            with open(percorso_input, 'r', encoding='utf-8') as f:
                testo_completo = f.read()
                
            # Applica il taglio per articoli
            lista_chunks = dividi_per_articoli(testo_completo)
            
            # Crea la struttura dati finale con i metadati
            struttura_dati = {
                "documento_origine": nome_file,
                "totale_frammenti": len(lista_chunks),
                "frammenti": lista_chunks
            }
            
            # Salva il risultato in un file JSON
            with open(percorso_output, 'w', encoding='utf-8') as f:
                json.dump(struttura_dati, f, ensure_ascii=False, indent=4)
                
            print(f"✂️ Tagliato: {nome_file} -> {len(lista_chunks)} frammenti creati.")
            file_processati += 1
            totale_chunks_generati += len(lista_chunks)
            
        except Exception as e:
            print(f"❌ Errore durante il chunking di {nome_file}: {e}")

print(f"\n*** CHUNKING COMPLETATO! ***")
print(f"File elaborati: {file_processati}")
print(f"Totale frammenti (chunks) generati pronti per l'AI: {totale_chunks_generati}")