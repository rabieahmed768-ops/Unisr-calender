from datetime import datetime
from flask import Flask, Response, request
import icalendar
import requests

app = Flask(__name__)

# NOTA: Questo è uno schema di base per interfacciarsi con EasyAcademy.
# Le URL esatte deiPOST/GET dipendono dai parametri specifici del portale UniSR.


@app.route("/ics")
def generate_ics():
corso = request.args.get("corso")
anno = request.args.get("anno")
linea = request.args.get("linea")

if not corso or not anno:
return "Parametri mancanti (corso, anno, linea)", 400

# 1. Qui va inserita la chiamata logica alle API o al backend di EasyAcademy di UniSR
# Esempio fittizio di richiesta dati al portale UniSR:
# r = requests.post("https://orario.unisr.it/portale/index.php", data={...})
# lezioni = analizza_risposta(r.text)

# 2. Creazione del calendario iCalendar
cal = icalendar.Calendar()
cal.add("prodid", "-//UniSR Calendar Generator//it//")
cal.add("version", "2.0")

# Esempio di aggiunta di una lezione fittizia (da sostituire con i dati reali parsati)
event = icalendar.Event()
event.add("summary", "Anatomia I (Prof. Rossi)")
event.add(
"dtstart", datetime(2026, 11, 10, 9, 0, 0)
) # Anno, Mese, Giorno, Ora, Minuto
event.add("dtend", datetime(2026, 11, 10, 11, 0, 0))
event.add("location", "Aula Magna - Via Olgettina")
event.add(
"description", "Lezione frontale di Anatomia. Docente: Prof. Rossi"
)
cal.add_component(event)

# Restituisce il file .ics pronto per l'iscrizione sul calendario
response = Response(cal.to_ical(), mimetype="text/calendar")
response.headers["Content-Disposition"] = (
'attachment; filename="orario_unisr.ics"'
)
return response


if __name__ == "__main__":
app.run(debug=True)
