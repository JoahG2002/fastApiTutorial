from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import app.modellen
from app.databasis import engine  # één map vooruit
from app.routers import bericht
from app.routers import gebruiker
from app import authenticatie
from app.routers import like


app.modellen.Base.metadata.create_all(bind=engine)

app: FastAPI = FastAPI()

TOEGESTANE_DOMEINEN: list[str] = ['*']  # "https://www.google.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=TOEGESTANE_DOMEINEN,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(bericht.router)
app.include_router(gebruiker.router)
app.include_router(authenticatie.router)
app.include_router(like.router)


@app.get("/")  # een http-methode
async def root() -> dict[str, str]:
    """
    Deze functie behandelt verzoeken van de hoofdpagina van de website,
    en stuurt de data terug naar de gebruiker.
    """
    return {"bericht": "Welkom, n****!"}


def main() -> None:
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
