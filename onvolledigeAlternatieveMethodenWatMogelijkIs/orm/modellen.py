from databasis import Base
from sqlalchemy import Column, VARCHAR, Boolean, TIMESTAMP, text, func


class Berichttabel(Base):
    __tablename__: str = "BerichtenOrm"  # create de tabel (alleen als er nog geen is met dezelfde naam)

    id_: Column = Column(VARCHAR, primary_key=True, nullable=False)
    titel: Column = Column(VARCHAR, nullable=False)
    inhoud: Column = Column(VARCHAR, nullable=False)
    is_gepubliceerd: Column = Column(Boolean, server_default=func.true())
    gecreeerd_op: Column = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
