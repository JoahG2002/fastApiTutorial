import random
from fastapi import FastAPI, status, HTTPException
import uvicorn
from psycopg2._psycopg import connection
from pydantic import BaseModel
from typing import Optional, Any
import psycopg2  # PostgresSQL
from psycopg2.extras import RealDictCursor
import time
from datetime import datetime


"""
Dit deel van de cursus ging aanvankelijk fout, omdat ik verbonden was met de verkeerde databasis en dit niet door had.
Om deze reden werken bepaalde functies dus niet feilloos; ik heb ze niet meer nagelopen.
"""


app: FastAPI = FastAPI()


def verbind_met_databasis() -> connection | connection:
    """
    Poogt te verbinden met de databasis en blijft dit iedere twee seconden doen, als dat niet lukt.
    """
    while True:
        try:
            connectie: connection | connection = psycopg2.connect(host="localhost", dbname="databasisStraatIs",
                                                                  user="postgres", password="Y+n&u*(L9HZ%xf2FW?GP<s",
                                                                  port=5432, cursor_factory=RealDictCursor)

            huidige_tijdstip: datetime = datetime.now()

            print(f"\nU bent succesvol verbonden met de databasis ({huidige_tijdstip.hour}.{huidige_tijdstip.minute} uur).\n")

            return connectie

        except Exception as fouttype:
            print(f"\nEr is een fout opgetreden van type: {fouttype}.")
            print("U bent niet verbonden met de databasis.\n")

            time.sleep(3)
            print(f"\nOpnieuw proberen ...\n")


class Bericht(BaseModel):  # BaseModel valideert automatisch
    titel: str
    inhoud: str
    id: str
    is_gepubliceerd: bool = True   # standaardwaarde
    beoordeling: Optional[int] = None  # standaardwaarde


@app.get("/")  # een http-methode
async def root() -> dict[str, str]:
    """
    Deze functie behandelt verzoeken van de hoofdpagina van de website, en stuurt de data terug naar de gebruiker.
    """
    return {"bericht": "Welkom, n****!"}


@app.get("/berichten")
def haal_alle_berichten_op() -> dict[str, list[tuple[Any, ...]]]:
    """
    Haalt alle berichten op van de databasis.
    """
    try:
        connectie: connection | connection = verbind_met_databasis()
        cursor = connectie.cursor()

        cursor.execute("""SELECT *
                          FROM public."Berichten" ; """)

        alle_berichten: list[tuple[Any, ...]] = cursor.fetchall()

        connectie.commit()
        cursor.close()
        connectie.close()

        return {"data": alle_berichten}

    except Exception as e:
        print(f"foutmelding: {e}")


@app.post("/berichten", status_code=status.HTTP_201_CREATED)  # 201 voor creatie
def plaats_bericht(bericht: Bericht) -> dict[str, tuple[Any, ...] | None]:
    """
    Plaatst een bericht op de site, en stuurt de data terug naar de gebruiker.
    """

    try:
        connectie: connection | connection = verbind_met_databasis()
        cursor = connectie.cursor()

        id_: str = genereer_id()

        cursor.execute(f"""INSERT INTO public."Berichten" (id, titel, inhoud, is_gepubliceerd)
                           VALUES (%s, %s, %s, %s)
                           RETURNING *; """,
                       (id_, bericht.titel, bericht.inhoud, bericht.is_gepubliceerd))   # f-string zijn niet veilig

        geplaatst_bericht: tuple[Any, ...] = cursor.fetchone()

        connectie.commit()

        cursor.close()
        connectie.close()

        return {"data": geplaatst_bericht}

    except Exception as fouttype:
        print(f"\nEr is een fout opgetreden tijdens de creatie van het bericht '{bericht.titel}' — van type: {fouttype}\n")


@app.get("/berichten/{id_}")
def haal_bericht_op(id_: str) -> dict[str, tuple[Any, ...]]:
    """
    Haalt een bericht op van de databasis — op basis van zijn id.
    """
    try:
        connectie: connection | connection = verbind_met_databasis()
        cursor = connectie.cursor()

        cursor.execute("""SELECT *
                                FROM public."Berichten"
                                WHERE id = %s ; """, (id_,))
        connectie.commit()

        bericht: tuple[Any, ...] = cursor.fetchone()

        cursor.close()
        connectie.close()

        return {"data": bericht}

    except Exception as fouttype:
        print(f"\nEr is een fout opgetreden tijdens het ophalen van bericht {id_}. Het fouttype: {fouttype}.\n")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@app.delete("/berichten/{id_}")
def verwijder_bericht(id_: str) -> None:
    """
    Verwijderd een bericht — op basis van zijn id.
    """
    connectie: connection | connection = verbind_met_databasis()
    cursor = connectie.cursor()

    cursor.execute("""DELETE
                            FROM public."Berichten"
                            WHERE id = %s 
                            RETURNING * ; """, (id_,))

    verwijderd_bericht: tuple[Any, ...] = cursor.fetchone()

    connectie.commit()

    cursor.close()
    connectie.close()

    if verwijderd_bericht:
        return None
    else:
        print(f"\nEr is een fout opgetreden tijdens het ophalen van bericht {id_}.\n")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@app.put("/berichten/{id_}")
def wijzig_bericht(id_: str, bericht: Bericht) -> dict[str, tuple[Any, ...]]:
    """
    Update een bericht — op basis van zijn id.
    """
    connectie: connection | connection = verbind_met_databasis()
    cursor = connectie.cursor()

    cursor.execute("""UPDATE public."Berichten"
                            SET titel = %s, inhoud = %s, is_gepubliceerd = %s
                            WHERE id = %s
                            RETURNING * ; """,
                   (bericht.titel, bericht.inhoud, bericht.is_gepubliceerd, id_))

    gewijzigd_bericht: tuple[Any, ...] = cursor.fetchone()

    connectie.commit()

    cursor.close()
    connectie.close()

    if gewijzigd_bericht:
        return {"data": gewijzigd_bericht}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Het bericht {id_} is niet gevonden.")


def genereer_id() -> str:
    """
    Genereert een willekeurig id.
    """
    id_als_lijst: list[str] = [str(random.randint(0, 9)) for _ in range(0, 16)]
    id_: str = ''.join(id_als_lijst)

    return id_


def main() -> None:
    uvicorn.run("main_sql:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
