from datetime import datetime
from flask import Flask, Response, request
import icalendar
import requests

app = Flask(__name__)


@app.route("/")
def home():
return (
"Server Calendario UniSR attivo! Usa l'endpoint /ics?corso=...&anno=...&linea=..."
" per generare il calendario."
)


@app.route("/ics")
def generate_ics():
# Riceve i parametri dall'utente (es. /ics?corso=medicina&anno=1&linea=A)
corso = request.args.get("corso")
anno = request.args.get("anno")
linea = request.args.get("linea", "")

if not corso or not anno:
return (
"Errore: Specifica almeno i parametri 'corso' e 'anno'."
" Esempio: /ics?corso=medicina&anno=1",
400,
)

# ---------------------------------------------------------
# QUI VA INSERITA LA LOGICA PER SCARICARE I DATI DA UNISR
# ---------------------------------------------------------
# Esempio: Puoi effettuare una richiesta HTTP al portale EasyAcademy di UniSR
# url_unisr = f"https://orario.unisr.it/portale/index.php?..."
# risposta = requests.get(url_unisr)
# (Qui analizzeresti la risposta con BeautifulSoup per estrarre le lezioni)

# Per adesso, inseriamo una struttura dati di esempio dinamica basata sui parametri:
cal = icalendar.Calendar()
cal.add("prodid", f"-//UniSR Calendar - {corso}//it//")
cal.add("version", "2.0")

# Esempio di lezione generata dinamicamente in base ai parametri scelti
event = icalendar.Event()
event.add(
"summary", f"Lezione di prova per {corso.upper()} (Anno {anno})"
)
event.add("dtstart", datetime(2026, 11, 15, 10, 0, 0))
event.add("dtend", datetime(2026, 11, 15, 12, 0, 0))
event.add("location", f"Aula virtuale - Linea {linea or 'Unica'}")
event.add(
"description",
"Orario generato automaticamente dal server personalizzato UniSR.",
)
cal.add_component(event)

# Restituisce il file .ics formattato per Apple/Google Calendar
response = Response(cal.to_ical(), mimetype="text/calendar")
response.headers["Content-Disposition"] = (
f'attachment; filename="orario_{corso}_{anno}.ics"'
)
return response


if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)
