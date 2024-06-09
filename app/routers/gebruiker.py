from fastapi import Depends, status, HTTPException, APIRouter
from pydantic import EmailStr
from sqlalchemy.orm import Session
from .. import modellen
from ..databasis import haal_databasis_op
from ..schemas import CreeerGebruiker, GebruikerAlsReactie, Gebruiker
from ..ondersteuning import genereer_id, hash_wachtwoord


router: APIRouter = APIRouter(
    prefix="/gebruikers",
    tags=["Gebruikers"]  # documentatietitel
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GebruikerAlsReactie)
def creeer_gebruiker(gebruiker: CreeerGebruiker, databasis: Session = Depends(haal_databasis_op)) -> GebruikerAlsReactie:
    """
    Creëert een gebruiker op basis van haar invoer.
    """
    nieuwe_gebruiker: CreeerGebruiker = modellen.Gebruikertabel(**gebruiker.dict())
    nieuwe_gebruiker.id_ = genereer_id()
    nieuwe_gebruiker.wachtwoord = hash_wachtwoord(nieuwe_gebruiker.wachtwoord)

    databasis.add(nieuwe_gebruiker)
    databasis.commit()
    databasis.refresh(nieuwe_gebruiker)
    databasis.close()

    reactiedata: dict[str, str | EmailStr] = {
        "id_": gebruiker.id_,
        "e_mail": gebruiker.e_mail,
        "volledige_naam": gebruiker.volledige_naam
    }

    return GebruikerAlsReactie(**reactiedata)


@router.get("/{id_}", response_model=Gebruiker)
def haal_gebruiker_op(id_: str, databasis: Session = Depends(haal_databasis_op)) -> Gebruiker:
    """
    Haalt de data van een gebruiker op — op basis van haar id.
    """
    gebruikerdata: Gebruiker = databasis.query(modellen.Gebruikertabel).filter(modellen.Gebruikertabel.id_ == id_).first()

    databasis.close()

    if gebruikerdata:
        return gebruikerdata
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gebruiker {id_} is niet gevonden.")
