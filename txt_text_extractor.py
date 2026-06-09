import os
import fitz  # È il nome tecnico della libreria PyMuPDF che abbiamo installato

# 1. Definiamo dove sono i file originali e dove salvare i risultati
cartella_pdf = "PDF_Originali"
cartella_output = "Testi_Estratti"

# 2. Iniziamo il ciclo: il programma guarda ogni file nella cartella
print("Inizio l'estrazione dei testi. Potrebbe volerci qualche minuto...\n")

for nome_file in os.listdir(cartella_pdf):
    # Controlliamo che sia effettivamente un file PDF
    if nome_file.lower().endswith(".pdf"):
        percorso_pdf = os.path.join(cartella_pdf, nome_file)
        testo_completo = ""
        
        try:
            # Apriamo il PDF
            documento = fitz.open(percorso_pdf)
            
            # Leggiamo ogni pagina e uniamo il testo
            for pagina in documento:
                testo_completo += pagina.get_text()
            
            # Creiamo il nome per il nuovo file di testo (es. da "decreto.pdf" a "decreto.txt")
            nome_txt = nome_file.replace(".pdf", ".txt")
            percorso_txt = os.path.join(cartella_output, nome_txt)
            
            # Salviamo il testo pulito nel nuovo file
            with open(percorso_txt, "w", encoding="utf-8") as file_testo:
                file_testo.write(testo_completo)
                
            print(f"✅ Letto e salvato: {nome_file}")
            
        except Exception as errore:
            print(f"❌ Impossibile leggere {nome_file}. Errore: {errore}")

print("\n*** OPERAZIONE COMPLETATA! ***")