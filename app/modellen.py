from .databasis import Base
from sqlalchemy import Column, VARCHAR, Boolean, TIMESTAMP, text, ForeignKey


class Berichttabel(Base):
    __tablename__: str = "BerichtenOrm"  # create de tabel (alleen als er nog geen is met dezelfde naam)

    id_: Column = Column(VARCHAR, primary_key=True, nullable=False)
    titel: Column = Column(VARCHAR, nullable=False)
    inhoud: Column = Column(VARCHAR, nullable=False)
    is_gepubliceerd: Column = Column(Boolean, server_default="TRUE")
    gecreeerd_op: Column = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    gebruiker_id: Column = Column(VARCHAR, ForeignKey("Gebruikers.id_", ondelete="CASCADE"), nullable=False)


class Gebruikertabel(Base):
    __tablename__: str = "Gebruikers"

    id_: Column = Column(VARCHAR, primary_key=True, nullable=False)
    e_mail: Column = Column(VARCHAR, nullable=False, unique=True)
    wachtwoord: Column = Column(VARCHAR, nullable=False)
    volledige_naam: Column = Column(VARCHAR, nullable=False)
    gecreeerd_op: Column = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))


class Liketabel(Base):
    __tablename__: str = "Likes"

    gebruiker_id: Column = Column(VARCHAR, ForeignKey("Gebruikers.id_", ondelete="CASCADE"), primary_key=True, nullable=False)
    bericht_id: Column = Column(VARCHAR, ForeignKey("BerichtenOrm.id_", ondelete="CASCADE"), primary_key=True, nullable=False)
