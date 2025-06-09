from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

load_dotenv()  # carica variabili da .env se presente

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def convertitore():
    risultato = None
    if request.method == 'POST':
        valore = float(request.form['valore'])
        tipo = request.form['tipo']
        if tipo == 'CtoF':
            risultato = round(valore * 9 / 5 + 32, 2)
        elif tipo == 'FtoC':
            risultato = round((valore - 32) * 5 / 9, 2)
        elif tipo == 'mToKm':
            risultato = round(valore / 1000, 4)
        elif tipo == 'kmToM':
            risultato = round(valore * 1000, 2)
    return render_template('convert.html', risultato=risultato)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
