import os
re_import = __import__('re')
from datetime import datetime, timedelta
from flask import Flask, Response, request
import icalendar
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scarica_orari_da_unisr(corso, anno, linea_richiesta):
    """
    Esegue il parsing dei prossimi 30 giorni da EasyAcademy UniSR
    rispettando le preferenze di formattazione (Aula come titolo/luogo, Materia e Docente nei dettagli).
    """
    eventi = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    oggi = datetime.now()
    
    # Cicla sui prossimi 30 giorni per coprire un intero mese
    for i in range(30):
        giorno_target = oggi + timedelta(days=i)
        data_str = giorno_target.strftime("%d/%m/%Y")
        
        url_target = f"https://orario.unisr.it/default.asp?ext=ok&data={data_str}&CDS_ID=10324&DAORA=0&ANNO_CORSO=2&id_palazzo=0&lezioni=ok&esami=ok"
        
        try:
            risposta = requests.get(url_target, headers=headers, timeout=5)
            
            if risposta.status_code == 200:
                soup = BeautifulSoup(risposta.text, 'html.parser')
                righe = soup.find_all('tr')
                
                aula_corrente = "Campus UniSR - Aula Studio"
                
                for row in righe:
                    testo_riga = row.get_text(separator=" ", strip=True)
                    
                    if "Aula" in testo_riga or "VASARI" in testo_riga:
                        aula_corrente = testo_riga[:60]
                    
                    if re_import.search(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', testo_riga):
                        if linea_richiesta.lower() in testo_riga.lower():
                            match_orario = re_import.search(r'(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})', testo_riga)
                            if match_orario:
                                h_in, m_in, h_fin, m_fin = map(int, match_orario.groups())
                                
                                dt_inizio = datetime(giorno_target.year, giorno_target.month, giorno_target.day, h_in, m_in, 0)
                                dt_fine = datetime(giorno_target.year, giorno_target.month, giorno_target.day, h_fin, m_fin, 0)
                                
                                # Estrae materia e docente in modo pulito
                                mat_match = re_import.search(r'Lezione:\s*([^()]+)', testo_riga)
                                materia = mat_match.group(1).strip() if mat_match else "Lezione UniSR"
                                
                                doc_match = re_import.search(r'docente:\s*([^)]+)', testo_riga, re_import.IGNORECASE)
                                docente = doc_match.group(1).strip() if doc_match else "N.D."
                                
                                eventi.append({
                                    "titolo": aula_corrente,
                                    "location": aula_corrente,
                                    "descrizione": f"Materia: {materia} | Docente: {docente}",
                                    "inizio": dt_inizio,
                                    "fine": dt_fine
                                })
        except Exception as e:
            print(f"Errore nello scraping per il giorno {data_str}: {e}")
            continue

    # Fallback se non trova eventi nel mese (es. periodi di pausa)
    if not eventi:
        eventi.append({
            "titolo": "VASARI - Aula VA202",
            "location": "VASARI - Aula VA202",
            "descrizione": "Materia: Nessuna lezione programmata | Docente: N.D.",
            "inizio": datetime(oggi.year, oggi.month, oggi.day, 13, 30, 0),
            "fine": datetime(oggi.year, oggi.month, oggi.day, 15, 30, 0)
        })
            
    return eventi

@app.route("/")
def home():
    return "Server Calendario UniSR - Sincronizzazione Mensile Attiva!"

@app.route("/ics")
def generate_ics():
    corso = request.args.get("corso", "medicina")
    anno = request.args.get("anno", "2")
    linea = request.args.get("linea", "rossa")
    
    cal = icalendar.Calendar()
    cal.add("prodid", f"-//UniSR Calendar - Medicina e Chirurgia Anno {anno}//it//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", f"UniSR Medicina 2° ({linea.capitalize()})")

    lezioni = scarica_orari_da_unisr(corso, anno, linea)

    for lezione in lezioni:
        event = icalendar.Event()
        event.add("summary", lezione["titolo"])
        event.add("dtstart", lezione["inizio"])
        event.add("dtend", lezione["fine"])
        event.add("location", lezione["location"])
        event.add("description", lezione["descrizione"])
        cal.add_component(event)

    response = Response(cal.to_ical(), mimetype="text/calendar")
    # Aggiungiamo intestazioni per suggerire al client di rinfrescare spesso
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Content-Disposition"] = f'attachment; filename="orario_medicina_{linea}.ics"'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
