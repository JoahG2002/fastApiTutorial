import random
from fastapi import FastAPI, Depends, status, HTTPException
import uvicorn
from typing import Type, Optional
from pydantic import BaseModel
import modellen
from databasis import engine, haal_databasis_op
from sqlalchemy.orm import Session


modellen.Base.metadata.create_all(bind=engine)


app: FastAPI = FastAPI()


class Bericht(BaseModel):  # BaseModel valideert automatisch
    titel: str
    inhoud: str
    id: str
    is_gepubliceerd: bool = True
    beoordeling: Optional[int] = None


@app.get("/")  # een http-methode
async def root() -> dict[str, str]:
    """
    Deze functie behandelt verzoeken van de hoofdpagina van de website, en stuurt de data terug naar de gebruiker.
    """
    return {"bericht": "Welkom, n****!"}


@app.get("/sqlalchemy")
def haal_alle_berichten_op(databasis: Session = Depends(haal_databasis_op)) -> dict[str, list[dict[str, object]]]:
    """
    Haalt alle berichten in de databasis op.
    """
    alle_berichten: list[Type[modellen.Berichttabel]] = databasis.query(modellen.Berichttabel).all()
    verwerkte_berichten: list[dict[str, object]] = [{"id": bericht.id_, "titel": bericht.titel, "inhoud": bericht.inhoud, "is_gepubliceerd": bericht.is_gepubliceerd} for bericht in alle_berichten]

    return {"data": verwerkte_berichten}


@app.post("/berichten", status_code=status.HTTP_201_CREATED)
def creeer_bericht(nieuw_bericht: Bericht, databasis: Session = Depends(haal_databasis_op)) -> None:
    """
    Creëert een nieuw bericht.
    """
    id_bericht: str = genereer_id()

    nieuw_bericht_: object = modellen.Berichttabel(titel=nieuw_bericht.titel, inhoud=nieuw_bericht.inhoud, id_=id_bericht, is_gepubliceerd=True)  # alternatief: **post.dict()

    databasis.add(nieuw_bericht_)
    databasis.commit()
    databasis.refresh(nieuw_bericht_)
    databasis.close()


@app.get("/berichten/{id_}")
def haal_bericht_op(id_: str, databasis: Session = Depends(haal_databasis_op)) -> dict[str, dict[str, str | bool]]:
    """
    Haalt een bericht op — op basis van zijn id.
    """
    bericht: Bericht = databasis.query(modellen.Berichttabel).filter(modellen.Berichttabel.id_ == id_).first()

    if bericht:
        # voorkomt serialisation-foutmelding
        bericht_als_dictionary: dict[str, str | bool] = {
            "id": bericht.id_,
            "titel": bericht.titel,
            "inhoud": bericht.inhoud,
            "is_gepubliceerd": bericht.is_gepubliceerd
        }
        return {"data": bericht_als_dictionary}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@app.delete("/berichten/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def verwijder_bericht(id_: str, databasis: Session = Depends(haal_databasis_op)) -> None:
    """
    Verwijdert een bericht — op basis van zijn id.
    """
    bericht: Bericht = databasis.query(modellen.Berichttabel).filter(modellen.Berichttabel.id_ == id_).first()

    if bericht:
        bericht.delete(synchronize_session=False)

        databasis.commit()
        databasis.refresh(bericht)
        databasis.close()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@app.put("/berichten/{id_}")
def update_bericht(id_: str, bericht: Bericht, databasis: Session = Depends(haal_databasis_op)) -> dict[str, dict[str, str | bool]]:
    """
    Update een bericht — op basis van zijn id.
    """
    opgevraagd_bericht: Bericht = databasis.query(modellen.Berichttabel).filter(modellen.Berichttabel.id_ == id_).first()

    if opgevraagd_bericht:
        opgevraagd_bericht.titel = bericht.titel
        opgevraagd_bericht.inhoud = bericht.inhoud

        databasis.commit()
        databasis.refresh(opgevraagd_bericht)
        databasis.close()

        return {"aangepast bericht": {"id": opgevraagd_bericht.id_, "titel": opgevraagd_bericht.titel,
                                      "inhoud": opgevraagd_bericht.inhoud, "is_gepubliceerd": opgevraagd_bericht.is_gepubliceerd}}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


def genereer_id() -> str:
    """
    Genereert een willekeurig id.
    """
    id_als_lijst: list[str] = [str(random.randint(0, 9)) for _ in range(0, 16)]
    id_: str = ''.join(id_als_lijst)

    return id_


def main() -> None:
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
