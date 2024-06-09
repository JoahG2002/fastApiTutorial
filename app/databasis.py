from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .configureer import instellingen


SQLALCHEMY_DATABASISLINK: str = f"postgresql://{instellingen.gebruikersnaam_databasis}:{instellingen.wachtwoord_databasis}@{instellingen.hostnaam_databasis}/{instellingen.naam_databasis}"

engine: Engine = create_engine(SQLALCHEMY_DATABASISLINK)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def haal_databasis_op() -> Session:
    """
    Haalt de databasis op.
    """
    databasis: Session = SessionLocal()

    try:
        yield databasis
    finally:
        databasis.close()
