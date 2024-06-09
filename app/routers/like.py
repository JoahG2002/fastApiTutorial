from fastapi import APIRouter, status, HTTPException, Depends
from ..schemas import Like, Tokendata
from .. import modellen
from ..databasis import haal_databasis_op
from sqlalchemy.orm import Session
from .. import authenticatie


router: APIRouter = APIRouter(
    prefix="/likes",
    tags=["Gebruikers"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def like_bericht(like: Like, databasis: Session = Depends(haal_databasis_op),
                 huidige_gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker)) -> dict[str, str]:
    """
    Like een bericht — als het bestaat en de gebruiker het nog niet heeft geliket.
    """
    gevonden_like: modellen.Liketabel = databasis.query(modellen.Liketabel).filter(
        modellen.Liketabel.bericht_id == like.bericht_id, modellen.Liketabel.gebruiker_id == huidige_gebruiker.id_
    ).first()

    if like.like_dislike == 1:
        if gevonden_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Gebruiker {huidige_gebruiker.id_} heeft dit bericht ({like.bericht_id}) reeds geliket.")
        else:
            nieuwe_like: modellen.Liketabel = modellen.Liketabel(bericht_id=like.bericht_id, gebruiker_id=huidige_gebruiker.id_)

            databasis.add(nieuwe_like)
            databasis.commit()
            databasis.close()

            return {"bericht": "Bericht succesvol geliket."}
    else:
        databasis.delete(gevonden_like)
        databasis.commit()
        databasis.close()

        return {"bericht": "Bericht succesvol disliket."}
