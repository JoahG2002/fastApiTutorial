from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func, Row
from .. import modellen  # één map terug
from ..databasis import haal_databasis_op
from ..schemas import CreeerBericht, BerichtAlsReactie, Berichtbasis, UpdateBericht, Tokendata, BerichtMetLikes
from ..ondersteuning import genereer_id
from .. import authenticatie
from typing import Optional, List, Any


router: APIRouter = APIRouter(
    tags=["Berichten"]  # documentatietitel
)


@router.get("/sqlalchemy", response_model=List[BerichtMetLikes])
def haal_alle_berichten_op(databasis: Session = Depends(haal_databasis_op), gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker),
                           limiet: int = 30, zoekterm: Optional[str] = '') -> List[BerichtMetLikes]:
    """
    Haalt alle berichten van een specifieke gebruiker op in de databasis op.
    """
    alle_berichten_gebruiker_met_likes: List[Row[tuple[modellen.Berichttabel, int]]] = (
        databasis.query(
            modellen.Berichttabel,
            func.count(modellen.Liketabel.bericht_id).label("aantal_likes")
        )
        .join(modellen.Liketabel, modellen.Liketabel.bericht_id == modellen.Berichttabel.id_, isouter=True)
        .group_by(modellen.Berichttabel.id_)
        .filter(modellen.Berichttabel.titel.contains(zoekterm))
        .limit(limiet)
    ).all()

    berichten_van_gebruiker_met_likes: List[BerichtMetLikes] = []

    for bericht, aantal_likes in alle_berichten_gebruiker_met_likes:
        berichtdata: dict[str, Any] = {
            "id_": bericht.id_,
            "gebruiker_id": bericht.gebruiker_id,
            "titel": bericht.titel,
            "inhoud": bericht.inhoud,
            "is_gepubliceerd": bericht.is_gepubliceerd,
            "aantal_likes": aantal_likes
        }

        berichtdata_als_object: BerichtMetLikes = BerichtMetLikes(**berichtdata)
        berichten_van_gebruiker_met_likes.append(berichtdata_als_object)

    return berichten_van_gebruiker_met_likes


@router.get("/berichten/{id_}", response_model=BerichtMetLikes)
def haal_bericht_op(id_: str, databasis: Session = Depends(haal_databasis_op), gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker)
                    ) -> BerichtMetLikes:
    """
    Haalt een bericht op — op basis van zijn id.
    """
    bericht: tuple[modellen.Berichttabel, int] = (
        databasis.query(
            modellen.Berichttabel,
            func.count(modellen.Liketabel.bericht_id).label("aantal_likes")
        )
        .join(modellen.Liketabel, modellen.Liketabel.bericht_id == modellen.Berichttabel.id_, isouter=True)
        .group_by(modellen.Berichttabel.id_)
        .filter(modellen.Berichttabel.id_ == id_)
    ).first()

    berichtdata: Berichtbasis = bericht[0]
    aantal_likes: int = bericht[1]

    if bericht and (berichtdata.gebruiker_id == gebruiker.id_):
        reactiedata: dict[str, str | bool] = {
            "id_": berichtdata.id_,
            "gebruiker_id": gebruiker.id_,
            "titel": berichtdata.titel,
            "inhoud": berichtdata.inhoud,
            "is_gepubliceerd": berichtdata.is_gepubliceerd,
            "aantal_likes": aantal_likes
        }

        return BerichtMetLikes(**reactiedata)
    elif (bericht or (bericht is None)) and (gebruiker.id_ != berichtdata.gebruiker_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"U hebt geen toegang tot dit bericht.")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@router.post("/berichten", status_code=status.HTTP_201_CREATED, response_model=BerichtAlsReactie)
def plaats_bericht(nieuw_bericht: CreeerBericht, databasis: Session = Depends(haal_databasis_op),
                   gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker)) -> BerichtAlsReactie:
    """
    Creëert een nieuw bericht — als de gebruiker succesvol is ingelogd.
    """
    id_bericht: str = genereer_id()

    nieuw_bericht_: object = modellen.Berichttabel(titel=nieuw_bericht.titel, inhoud=nieuw_bericht.inhoud, id_=id_bericht, gebruiker_id=gebruiker.id_, is_gepubliceerd=True)  # alternatief: **post.dict()

    databasis.add(nieuw_bericht_)
    databasis.commit()
    databasis.refresh(nieuw_bericht_)
    databasis.close()

    reactiedata: dict[str, str | bool | int] = {
        "id_": nieuw_bericht.id_,
        "gebruiker_id": gebruiker.id_,
        "titel": nieuw_bericht.titel,
        "inhoud": nieuw_bericht.inhoud,
        "is_gepubliceerd": nieuw_bericht.is_gepubliceerd
    }

    return BerichtAlsReactie(**reactiedata)


@router.delete("/berichten/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def verwijder_bericht(id_: str, databasis: Session = Depends(haal_databasis_op), gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker)
                      ) -> None:
    """
    Verwijdert een bericht — op basis van zijn id.
    """
    bericht: Berichtbasis = databasis.query(modellen.Berichttabel).filter(modellen.Berichttabel.id_ == id_).first()

    if bericht and (gebruiker.id_ == bericht.gebruiker_id):
        bericht.delete(synchronize_session=False)

        databasis.commit()
        databasis.refresh(bericht)
        databasis.close()
    elif (bericht or (bericht is None)) and (gebruiker.id_ != bericht.gebruiker_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"U hebt geen toegang tot dit bericht.")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")


@router.put("/berichten/{id_}")
def update_bericht(id_: str, bericht: UpdateBericht, databasis: Session = Depends(haal_databasis_op), gebruiker: Tokendata = Depends(authenticatie.geef_huidige_gebruiker)
                   ) -> BerichtAlsReactie:
    """
    Update een bericht — op basis van zijn id.
    """
    opgevraagd_bericht: UpdateBericht = databasis.query(modellen.Berichttabel).filter(modellen.Berichttabel.id_ == id_).first()

    if opgevraagd_bericht and (bericht.gebruiker_id == gebruiker.id_):
        opgevraagd_bericht.titel = bericht.titel
        opgevraagd_bericht.inhoud = bericht.inhoud

        databasis.commit()
        databasis.refresh(opgevraagd_bericht)
        databasis.close()

        reactiedata: dict[str, str | bool] = {
            "id_": opgevraagd_bericht.id_,
            "gebruiker_id": opgevraagd_bericht.gebruiker_id,
            "titel": opgevraagd_bericht.titel,
            "inhoud": opgevraagd_bericht.inhoud,
            "is_gepubliceerd": opgevraagd_bericht.is_gepubliceerd
        }

        return BerichtAlsReactie(**reactiedata)
    elif (bericht or (bericht is None)) and (gebruiker.id_ != bericht.gebruiker_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"U hebt geen toegang tot dit bericht.")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bericht {id_} is niet gevonden.")
