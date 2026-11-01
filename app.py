import os
from datetime import datetime
from flask import Flask, Response, request
import icalendar

app = Flask(__name__)

def ottieni_orari_unisr(corso, anno, linea):
  """
  Funzione ponte: qui dentro integreremo la chiamata a EasyAcademy (orario.unisr.it)
  per scaricare gli eventi reali filtrati per corso, anno e linea.
  Per ora restituisce una lista strutturata pronta per il calendario.
  """
  # Esempio di dati che arriveranno dal portale UniSR
  eventi_reali = [
    {
      "titolo": f"Lezione Ufficiale - {corso.upper()} ({anno}° Anno, Linea {linea.upper()})",
      "inizio": datetime(2026, 11, 16, 9, 0, 0),
      "fine": datetime(2026, 11, 16, 13, 0, 0),
      "aula": "Aula Lezioni - Campus UniSR (DIBIT)"
    }
  ]
  return eventi_reali

@app.route("/")
def home():
  return "Server Calendario UniSR attivo e ottimizzato!"

@app.route("/ics")
def generate_ics():
  # Legge i parametri dall'URL (es. /ics?corso=medicina&anno=2&linea=rossa)
  corso = request.args.get("corso", "medicina")
  anno = request.args.get("anno", "2")
  linea = request.args.get("linea", "rossa-viola")
  
  # Inizializza il calendario iCal
  cal = icalendar.Calendar()
  cal.add("prodid", f"-//UniSR Calendar - {corso} Anno {anno}//it//")
  cal.add("version", "2.0")
  cal.add("calscale", "GREGORIAN")
  cal.add("method", "PUBLISH")
  cal.add("x-wr-calname", f"UniSR {corso.capitalize()} {anno}° Anno ({linea})")
  
  # Recupera le lezioni tramite la funzione dedicata
  lezioni = ottieni_orari_unisr(corso, anno, linea)
  
  for lezione in lezioni:
    event = icalendar.Event()
    event.add("summary", lezione["titolo"])
    event.add("dtstart", lezione["inizio"])
    event.add("dtend", lezione["fine"])
    event.add("location", lezione["aula"])
    event.add("description", f"Sincronizzato automaticamente per {corso} - Linea {linea}")
    cal.add_component(event)
  
  response = Response(cal.to_ical(), mimetype="text/calendar")
  response.headers["Content-Disposition"] = f'attachment; filename="orario_{corso}_{anno}_{linea}.ics"'
  return response

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
