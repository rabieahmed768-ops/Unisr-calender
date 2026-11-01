import os
from datetime import datetime
from flask import Flask, Response, request
import icalendar

app = Flask(__name__)

@app.route("/")
def home():
  return "Server Calendario UniSR attivo - Medicina 2° Anno (Linea Rossa/Viola)!"

@app.route("/ics")
def generate_ics():
  corso = request.args.get("corso", "medicina").upper()
  anno = request.args.get("anno", "2")
  linea = request.args.get("linea", "rossa-viola").lower()
  
  cal = icalendar.Calendar()
  cal.add("prodid", f"-//UniSR Calendar - {corso} Anno {anno} Linea {linea}//it//")
  cal.add("version", "2.0")
  cal.add("calscale", "GREGORIAN")
  cal.add("method", "PUBLISH")
  cal.add("x-wr-calname", f"UniSR Medicina 2° ({linea.capitalize()})")
  
  # Dati di simulazione mirati per il tuo anno e linea (pronti per essere sostituiti dalla fetch di EasyAcademy)
  lezioni_medicina = [
    {
      "titolo": f"Lezione di Fisiologia / Patologia ({linea.upper()})",
      "inizio": datetime(2026, 11, 16, 9, 0, 0),
      "fine": datetime(2026, 11, 16, 12, 0, 0),
      "aula": "Aula Lezioni - DIBIT
    },
    {
      "titolo": f"Laboratorio Clinico ({linea.upper()})",
      "inizio": datetime(2026, 11, 17, 14, 0, 0),
      "fine": datetime(2026, 11, 17, 17, 0, 0),
      "aula": "Laboratorio Multimediale"
    }
  ]
  
  for lezione in lezioni_medicina:
    event = icalendar.Event()
    event.add("summary", lezione["titolo"])
    event.add("dtstart", lezione["inizio"])
    event.add("dtend", lezione["fine"])
    event.add("location", lezione["aula"])
    event.add("description", f"Orario ufficiale per Medicina, 2° anno, Linea {linea}.")
    cal.add_component(event)
  
  response = Response(cal.to_ical(), mimetype="text/calendar")
  response.headers["Content-Disposition"] = f'attachment; filename="orario_medicina_2_{linea}.ics"'
  return response

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
