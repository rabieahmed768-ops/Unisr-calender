import os
from datetime import datetime
from flask import Flask, Response, request
import icalendar
import requests

app = Flask(__name__)


@app.route("/")
def home():
return "Server Calendario UniSR attivo!"


@app.route("/ics")
def generate_ics():
corso = request.args.get("corso", "generico")
anno = request.args.get("anno", "1")
linea = request.args.get("linea", "")
cal = icalendar.Calendar()
cal.add("prodid", f"-//UniSR Calendar - {corso}//it//")
cal.add("version", "2.0")
event = icalendar.Event()
event.add("summary", f"Lezione {corso.upper()} (Anno {anno})")
event.add("dtstart", datetime(2026, 11, 15, 10, 0, 0))
event.add("dtend", datetime(2026, 11, 15, 12, 0, 0))
event.add("location", f"Aula virtuale - Linea {linea or 'Unica'}")
cal.add_component(event)
response = Response(cal.to_ical(), mimetype="text/calendar")
response.headers["Content-Disposition"] = (
f'attachment; filename="orario_{corso}_{anno}.ics"'
)
return response


if __name__ == "__main__":
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
