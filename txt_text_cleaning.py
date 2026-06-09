import os
import re

# ==========================================
# 1. CONFIGURAZIONE CARTELLE
# ==========================================
# Cartella dove si trovano i file grezzi estratti in precedenza
cartella_input = "Testi_Estratti"
# Nuova cartella dove salveremo i file disinfettati
cartella_output = "Testi_Puliti"

# Il sistema crea automaticamente la cartella di output se non esiste
if not os.path.exists(cartella_output):
    os.makedirs(cartella_output)

# ==========================================
# 2. MOTORE DI PULIZIA
# ==========================================
def applica_pulizia(testo_grezzo):
    # 1. Rimuove tabulazioni e spazi multipli orizzontali
    testo = re.sub(r'[ \t]+', ' ', testo_grezzo)
    
    # 2. Rimuove i numeri di pagina e i boilerplate standard
    # Cancella pattern come "Pag. 12", "Pagina 3 di 40" 
    testo = re.sub(r'(?i)pag(ina)?\.?\s*\d+(\s*di\s*\d+)?', '', testo)
    # Rimuove eventuali diciture ricorrenti (puoi aggiungere qui altre frasi da scartare)
    testo = re.sub(r'(?i)gazzetta ufficiale della repubblica italiana', '', testo)
    
    righe_pulite = []
    
    # 3. Analisi riga per riga
    for riga in testo.split('\n'):
        riga = riga.strip()
        
        # Salta le righe completamente vuote
        if not riga:
            continue
        
        # 4. Filtro Garbage: conta il rapporto tra caratteri speciali e testo normale
        lunghezza = len(riga)
        if lunghezza > 0:
            # Conta i caratteri che NON sono lettere o numeri
            speciali = sum(1 for c in riga if not c.isalnum() and not c.isspace())
            rapporto_speciali = speciali / lunghezza
            
            # Se più del 30% della riga è fatta di simboli strani, scartala
            if rapporto_speciali > 0.3:
                continue
                
        righe_pulite.append(riga)
        
    # 5. Ricompone il documento mantenendo un singolo ritorno a capo tra i paragrafi
    testo_finale = '\n'.join(righe_pulite)
    testo_finale = re.sub(r'\n{2,}', '\n', testo_finale)
    
    return testo_finale

# ==========================================
# 3. ESECUZIONE DEL PROCESSO MASSIVO
# ==========================================
print("Avvio la pulizia dei documenti...")
file_processati = 0

for nome_file in os.listdir(cartella_input):
    if nome_file.endswith(".txt"):
        percorso_input = os.path.join(cartella_input, nome_file)
        percorso_output = os.path.join(cartella_output, nome_file)
        
        try:
            # Legge il file grezzo
            with open(percorso_input, 'r', encoding='utf-8') as f:
                testo_originale = f.read()
                
            # Passa il testo al motore di pulizia
            testo_pulito = applica_pulizia(testo_originale)
            
            # Salva il risultato nella nuova cartella
            with open(percorso_output, 'w', encoding='utf-8') as f:
                f.write(testo_pulito)
                
            print(f"✅ Disinfettato: {nome_file}")
            file_processati += 1
            
        except Exception as e:
            print(f"❌ Errore durante la pulizia di {nome_file}: {e}")

print(f"\n*** OPERAZIONE COMPLETATA! Elaborati {file_processati} file. ***")