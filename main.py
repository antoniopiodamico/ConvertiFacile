import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1) Carica le variabili da .env (in particolare DATABASE_URL)
load_dotenv()

# 2) Prepara SQLAlchemy
DATABASE_URL = os.getenv('DATABASE_URL')
engine      = create_engine(DATABASE_URL)
Session     = sessionmaker(bind=engine)
Base        = declarative_base()

# 3) Definisci il modello
class Conversione(Base):
    __tablename__ = 'conversioni'
    id         = Column(Integer, primary_key=True)
    tipo       = Column(String, nullable=False)
    valore_in  = Column(Float,  nullable=False)
    risultato  = Column(Float,  nullable=False)

# 4) Crea la tabella se non esiste
Base.metadata.create_all(engine)

# 5) App Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def convertitore():
    risultato = None
    if request.method == 'POST':
        # Calcolo conversione
        valore = float(request.form['valore'])
        tipo   = request.form['tipo']
        if tipo == 'CtoF':
            risultato = round(valore * 9/5 + 32, 2)
        elif tipo == 'FtoC':
            risultato = round((valore - 32) * 5/9, 2)
        elif tipo == 'mToKm':
            risultato = round(valore / 1000, 4)
        elif tipo == 'kmToM':
            risultato = round(valore * 1000, 2)

        # Salva nel database
        session = Session()
        nuova = Conversione(tipo=tipo,
                             valore_in=valore,
                             risultato=risultato)
        session.add(nuova)
        session.commit()
        session.close()

    return render_template('convert.html', risultato=risultato)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
