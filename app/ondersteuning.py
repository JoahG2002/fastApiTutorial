import random
from passlib.context import CryptContext


context_wachtwoord: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def genereer_id() -> str:
    """
    Genereert een willekeurig id.
    """
    id_als_lijst: list[str] = [str(random.randint(0, 9)) for _ in range(0, 16)]
    id_: str = ''.join(id_als_lijst)

    return id_


def hash_wachtwoord(wachtwoord: str) -> str:
    """
    Hasht een wachtwoord met bcrypt.
    """
    wachtwoord_gehasht: str = context_wachtwoord.hash(wachtwoord)

    return wachtwoord_gehasht


def verifieer_wachtwoord(opgegeven_wachtwoord: str, hasht_juiste_wachtwoord: str) -> bool:
    """
    Ontvangt een door een gebruiker opgegeven wachtwoord en het juiste wachtwoord gehasht,
    en gaat na of het opgegeven wachtwoord gehasht gelijk is aan het juiste wachtwoord.
    """
    return context_wachtwoord.verify(opgegeven_wachtwoord, hasht_juiste_wachtwoord)
