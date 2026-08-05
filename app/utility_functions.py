from app import database, class_models, tb_models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
import secrets

def id_gen() -> str:
    return secrets.token_urlsafe(32)

