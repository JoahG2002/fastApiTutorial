from pydantic_settings import BaseSettings


class Instellingen(BaseSettings):
    hostnaam_databasis: str
    poort_databasis: str
    wachtwoord_databasis: str
    naam_databasis: str
    gebruikersnaam_databasis: str
    geheime_sleutel: str
    hashalgoritme: str
    toegangstokenhoudbaarheidstijd_sessie_minuten: int

    class Config:
        env_file: str = ".env"


instellingen: Instellingen = Instellingen()
