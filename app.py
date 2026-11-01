import os
from datetime import datetime
from flask import Flask, Response, request
import icalendar

app = Flask(__name__)

@app.route("/")
def home():
  return "Server Calendario UniSR attivo e pronto per il parsing!"

@app.route("/ics")
def generate_ics():
  corso = request.args.get("corso", "generico").upper()
  anno = request.args.get("anno", "1")
  
  cal = icalendar.Calendar()
  cal.add("prodid", f"-//UniSR Calendar - {corso} Anno {anno}//it//")
  cal.add("version", "2.0")
  cal.add("calscale", "GREGORIAN")
  cal.add("method", "PUBLISH")
  cal.add("x-wr-calname", f"Orario UniSR - {corso} (Anno {anno})")
  lezioni_esempio = [
    {
      "titolo": f"Lezione Ufficiale {corso}",
      "inizio": datetime(2026, 11, 16, 9, 0, 0),
      "fine": datetime(2026, 11, 16, 11, 0, 0),
      "aula": "Aula Magna - Campus UniSR"
    }
  ]
  for lezione in lezioni_esempio:
    event = icalendar.Event()
    event.add("summary", lezione["titolo"])
    event.add("dtstart", lezione["inizio"])
    event.add("dtend", lezione["fine"])
    event.add("location", lezione["aula"])
    event.add("description", f"Orario generato automaticamente per {corso}, Anno {anno}.")
    cal.add_component(event)
  
  response = Response(cal.to_ical(), mimetype="text/calendar")
  response.headers["Content-Disposition"] = f'attachment; filename="orario_{corso}_anno_{anno}.ics"'
  return response

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
