import os
import pymupdf4llm

# ==========================================
# 1. CONFIGURAZIONE CARTELLE
# ==========================================
cartella_pdf = "PDF_Originali"
cartella_output = "Markdown_Estratti"

if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)

# ==========================================
# 2. MOTORE DI ESTRAZIONE MARKDOWN
# ==========================================
print("Inizio l'estrazione in formato Markdown. Potrebbe volerci qualche minuto...\n")

file_processati = 0

for nome_file in os.listdir(cartella_pdf):
    if nome_file.lower().endswith(".pdf"):
        percorso_pdf = os.path.join(cartella_pdf, nome_file)
        nome_md = nome_file.replace(".pdf", ".md")
        percorso_md = os.path.join(cartella_output, nome_md)
        
        try:
            # Questa singola funzione legge il PDF, interpreta i titoli, 
            # formatta le tabelle e restituisce il testo in formato Markdown
            testo_md = pymupdf4llm.to_markdown(percorso_pdf)
            
            # Salva il file .md
            with open(percorso_md, "w", encoding="utf-8") as f:
                f.write(testo_md)
                
            print(f"✅ Convertito in Markdown: {nome_file}")
            file_processati += 1
            
        except Exception as errore:
            print(f"❌ Impossibile convertire {nome_file}. Errore: {errore}")

print(f"\n*** OPERAZIONE COMPLETATA! Convertiti {file_processati} file. ***")