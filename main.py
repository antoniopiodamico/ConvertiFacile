import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, Integer, Float, String, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# 1) Carica le variabili da .env (in particolare DATABASE_URL)
load_dotenv()

# 2) Prepara SQLAlchemy
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception("La variabile d'ambiente DATABASE_URL non è stata impostata.")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# 3) Definisci il modello (la struttura della tabella)
class Conversione(Base):
    __tablename__ = 'conversioni'
    id = Column(Integer, primary_key=True)
    tipo = Column(String, nullable=False)
    valore_in = Column(Float, nullable=False)
    risultato = Column(Float, nullable=False)

# 4) Crea la tabella nel database, solo se non esiste già
Base.metadata.create_all(engine)

# 5) App Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def convertitore():
    risultato_corrente = None

    if request.method == 'POST':
        session = Session()
        try:
            # Calcolo della conversione
            valore = float(request.form['valore'])
            tipo = request.form['tipo']

            if tipo == 'CtoF':
                risultato_corrente = round(valore * 9/5 + 32, 2)
            elif tipo == 'FtoC':
                risultato_corrente = round((valore - 32) * 5/9, 2)
            elif tipo == 'mToKm':
                risultato_corrente = round(valore / 1000, 4)
            elif tipo == 'kmToM':
                risultato_corrente = round(valore * 1000, 2)
            # --- NUOVE CONVERSIONI ---
            elif tipo == 'kgToLbs':
                risultato_corrente = round(valore * 2.20462, 2)
            elif tipo == 'lbsToKg':
                risultato_corrente = round(valore / 2.20462, 2)
            elif tipo == 'kmhToMph':
                risultato_corrente = round(valore * 0.621371, 2)
            elif tipo == 'mphToKmh':
                risultato_corrente = round(valore / 0.621371, 2)

            # Salva la nuova conversione nel database se il calcolo è andato a buon fine
            if risultato_corrente is not None:
                nuova_conversione = Conversione(
                    tipo=tipo,
                    valore_in=valore,
                    risultato=risultato_corrente
                )
                session.add(nuova_conversione)
                session.commit()

        except ValueError:
            risultato_corrente = "Errore: Inserisci un valore numerico valido."
            session.rollback()
        except Exception as e:
            risultato_corrente = f"Si è verificato un errore: {e}"
            session.rollback() # Annulla le modifiche in caso di errore
        finally:
            session.close() # Chiudi sempre la sessione

    # --- LETTURA DELLO STORICO (avviene sempre, sia in GET che in POST) ---
    session = Session()
    storico = []
    try:
        # Recupera le ultime 10 conversioni, ordinate per ID decrescente (dalla più recente)
        storico = session.query(Conversione).order_by(desc(Conversione.id)).limit(10).all()
    except Exception as e:
        print(f"Errore durante il recupero dello storico: {e}")
    finally:
        session.close()

    return render_template('convert.html', risultato=risultato_corrente, storico=storico)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
