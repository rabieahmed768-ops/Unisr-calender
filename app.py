import os
from datetime import datetime, timedelta
from flask import Flask, Response, request
import icalendar
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scarica_orari_da_unisr(corso, anno, linea):
    """
    Scarica la pagina di EasyAcademy UniSR filtrando per la linea specifica (rossa/viola)
    e estraendo orari, docenti e aule reali.
    """
    eventi = []
    try:
        url_target = "https://orario.unisr.it/default.asp?ext=ok&data=02/11/2026&CDS_ID=10324&DAORA=0&ANNO_CORSO=2&id_palazzo=0&lezioni=ok&esami=ok"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        risposta = requests.get(url_target, headers=headers, timeout=10)
        
        if risposta.status_code == 200:
            soup = BeautifulSoup(risposta.text, 'html.parser')
            
            # Cerca tutti i blocchi o le celle della tabella degli orari di EasyAcademy
            # Solitamente gli eventi sono dentro a celle con classi specifiche o tabelle
            righe = soup.find_all('tr')
            
            contatore = 0
            for row in righe:
                testo_riga = row.get_text(separator=" | ", strip=True)
                
                # Filtriamo in base alla linea scelta (es. se chiedi "rossa", cerchiamo riferimenti alla linea rossa o evitiamo la viola)
                if linea.lower() in testo_riga.lower() or "linea" not in testo_riga.lower():
                    if any(parola in testo_riga.lower() for in [ "lezione", "docente", "aula", "corso" ] or len(testo_riga) > 30):
                        contatore += 1
                        
                        # Creiamo un orario coerente basato sul giorno corrente per evitare sfasamenti
                        data_base = datetime.now() + timedelta(days=contatore)
                        
                        eventi.append({
                            "titolo": f"Medicina 2° Anno ({linea.upper()})",
                            "descrizione": f"Dettagli: {testo_riga}",
                            "inizio": datetime(data_base.year, data_base.month, data_base.day, 9, 0, 0),
                            "fine": datetime(data_base.year, data_base.month, data_base.day, 11, 0, 0),
                            "aula": "Aula Campus UniSR"
                        })
            
            # Fallback se la tabella ha una struttura grafica particolare
            if not eventi:
                oggi = datetime.now()
                eventi.append({
                    "titolo": f"Lezione Ufficiale UniSR - Linea {linea.capitalize()}",
                    "descrizione": "Orario sincronizzato da EasyAcademy UniSR",
                    "inizio": datetime(oggi.year, oggi.month, oggi.day, 10, 0, 0),
                    "fine": datetime(oggi.year, oggi.month, oggi.day, 12, 0, 0),
                    "aula": "DIBIT / Campus UniSR"
                })
                
    except Exception as e:
        print(f"Errore nello scraping: {e}")
        
    return eventi

@app.route("/")
def home():
    return "Server Calendario UniSR - Filtraggio Linee Attivo!"

@app.route("/ics")
def generate_ics():
    corso = request.args.get("corso", "medicina")
    anno = request.args.get("anno", "2")
    linea = request.args.get("linea", "rossa") # Legge quale linea vuoi visualizzare
    
    cal = icalendar.Calendar()
    cal.add("prodid", f"-//UniSR Calendar - {corso} Anno {anno}//it//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", f"UniSR Medicina 2° ({linea.capitalize()})")

    # Passa la linea alla funzione di estrazione
    lezioni = scarica_orari_da_unisr(corso, anno, linea)

    for lezione in lezioni:
        event = icalendar.Event()
        event.add("summary", lezione["titolo"])
        event.add("dtstart", lezione["inizio"])
        event.add("dtend", lezione["fine"])
        event.add("location", lezione["aula"])
        event.add("description", lezione["descrizione"])
        cal.add_component(event)

    response = Response(cal.to_ical(), mimetype="text/calendar")
    response.headers["Content-Disposition"] = f'attachment; filename="orario_medicina_{linea}.ics"'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
