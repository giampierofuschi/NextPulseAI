import os
import re

cartella_input = "Markdown_Estratti"
cartella_output = "Markdown_Puliti"

if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)

def pulisci_markdown(testo_md):
    # 1. Rimuove solo i numeri di pagina e intestazioni burocratiche ripetitive
    # (Aggiungi qui eventuali frasi che vedi ripetersi su ogni pagina dei tuoi decreti)
    testo = re.sub(r'(?i)pag(ina)?\.?\s*\d+(\s*di\s*\d+)?', '', testo_md)
    testo = re.sub(r'(?i)gazzetta ufficiale della repubblica italiana', '', testo)
    
    # 2. Rimuove gli eccessi di righe vuote (lascia massimo un doppio a capo per dividere i paragrafi)
    testo = re.sub(r'\n{3,}', '\n\n', testo)
    
    return testo

print("Avvio la pulizia leggera dei file Markdown...")
file_processati = 0

for nome_file in os.listdir(cartella_input):
    if nome_file.endswith(".md"):
        percorso_input = os.path.join(cartella_input, nome_file)
        percorso_output = os.path.join(cartella_output, nome_file)
        
        try:
            with open(percorso_input, 'r', encoding='utf-8') as f:
                testo_originale = f.read()
                
            testo_pulito = pulisci_markdown(testo_originale)
            
            with open(percorso_output, 'w', encoding='utf-8') as f:
                f.write(testo_pulito)
                
            print(f"✅ Pulito: {nome_file}")
            file_processati += 1
            
        except Exception as e:
            print(f"❌ Errore: {e}")

print(f"\n*** COMPLETATO! Elaborati {file_processati} file. ***")