from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Berichtbasis(BaseModel):  # BaseModel valideert datatypen automatisch
    titel: str
    inhoud: str
    id_: str
    gebruiker_id: str
    is_gepubliceerd: bool = True


class CreeerBericht(Berichtbasis):
    pass  # neemt verder alle eigenschappen van BerichtBasis over


class UpdateBericht(Berichtbasis):
    pass


class BerichtAlsReactie(Berichtbasis):  # wat wordt teruggestuurd
    tijdstip_opgevraagd: datetime = datetime.now()


class BerichtMetLikes(Berichtbasis):
    aantal_likes: int


class Gebruiker(BaseModel):
    id_: str
    e_mail: EmailStr
    wachtwoord: str
    volledige_naam: str
    gecreeerd_op: datetime


class CreeerGebruiker(BaseModel):
    id_: str
    e_mail: EmailStr
    wachtwoord: str
    volledige_naam: str


class GebruikerAlsReactie(BaseModel):
    id_: str
    e_mail: EmailStr
    volledige_naam: str  # niet het wachtwoord
    laatst_opgevraagd: datetime = datetime.now()


class GebruikerInloggen(BaseModel):
    e_mail: EmailStr
    wachtwoord: str


class Token(BaseModel):
    toegangstoken: str
    tokentype: str


class Tokendata(BaseModel):
    id_: Optional[str]


class Like(BaseModel):
    bericht_id: str
    like_dislike: int
