from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contributions, members
from app.database import engine
from app import tb_models

tb_models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only — allows any frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contributions.router)
app.include_router(members.router)

