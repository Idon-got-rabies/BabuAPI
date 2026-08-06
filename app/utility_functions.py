from app import database, class_models, tb_models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
import secrets

def id_gen() -> str:
    return secrets.token_urlsafe(6)

def num_val(length: int, val: str):

    if val.isnumeric():
        val_no_space = val.replace(' ', '')
        val_leng = len(val_no_space)
        if val_leng < length or val_leng > length:
            return False
        else:
            return True
    elif not val.isnumeric():
        return False


