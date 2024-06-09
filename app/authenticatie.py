from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from .databasis import haal_databasis_op
from .schemas import Gebruiker, Tokendata, Token
from . import modellen  # uit huidige map, haal modellen
from .ondersteuning import verifieer_wachtwoord
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from .configureer import instellingen


oath2_schema: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="login")


GEHEIME_SLEUTEL: str = instellingen.geheime_sleutel
ALGORITME: str = instellingen.hashalgoritme
TOEGANGSTOKEN_HOUDBAARHEIDSTIJD_SESSIE_IN_MINUTEN: int = int(instellingen.toegangstokenhoudbaarheidstijd_sessie_minuten)


router: APIRouter = APIRouter(
    tags=["Authenticatie"]
)


@router.post("/inloggen", response_model=Token)
def log_gebruiker_in(inlogdata_gebruiker: OAuth2PasswordRequestForm = Depends(), databasis: Session = Depends(haal_databasis_op)) -> Token:
    """
    Logt de gebruiker in en geeft een token terug — als haar e-mailadres (username) en wachtwoord (password) kloppen. In ieder ander geval wordt een 404-fout teruggestuurd.
    """
    data_gebruiker: Gebruiker = databasis.query(modellen.Gebruikertabel).filter(modellen.Gebruikertabel.e_mail == inlogdata_gebruiker.username).first()

    if data_gebruiker:
        if verifieer_wachtwoord(inlogdata_gebruiker.password, data_gebruiker.wachtwoord):
            toegangstoken: str = genereer_toegangstoken({"gebruiker_id": data_gebruiker.id_})
            gebruikertoken: Token = Token(**{"toegangstoken": toegangstoken, "tokentype": "drager"})

            return gebruikertoken
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalide inloggegevens.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalide inloggegevens.")


def genereer_toegangstoken(gebruikerdata: dict[str, str]) -> str:
    """
    Genereert een toegangstoken door de gebruikerdata te versleutelen.
    """
    versleutelde_data: dict[str, str | datetime] = gebruikerdata

    verloop_gebruikersessie: datetime = datetime.now() + timedelta(minutes=TOEGANGSTOKEN_HOUDBAARHEIDSTIJD_SESSIE_IN_MINUTEN)
    versleutelde_data["verloop_gebruikersessie"] = verloop_gebruikersessie.isoformat()

    toegangstoken: str = jwt.encode(versleutelde_data, key=GEHEIME_SLEUTEL, algorithm=ALGORITME)

    return toegangstoken


def verifieer_toegangstoken(toegangstoken: str, uitzondering_inloggegevens: HTTPException) -> Tokendata:
    """
    Verifieert een toegangstoken door de versleutelde data uit te pakken en het daaruitvoorkomende id te verifiëren.
    """
    try:
        versleutelde_data: dict[str, str] = jwt.decode(toegangstoken, GEHEIME_SLEUTEL, [ALGORITME])
        opgehaald_id: str = versleutelde_data["gebruiker_id"]

        if opgehaald_id:
            tokendata: Tokendata = Tokendata(id_=opgehaald_id)

            return tokendata

        else:
            raise uitzondering_inloggegevens
    except JWTError:
        raise uitzondering_inloggegevens


def geef_huidige_gebruiker(toegangstoken: str = Depends(oath2_schema)) -> Tokendata:
    """
    Geeft het id van de gebruiker terug – als het toegangstoken valide is.
    """
    uitzondering_inloggegevens: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalide inloggegevens",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return verifieer_toegangstoken(toegangstoken, uitzondering_inloggegevens)
