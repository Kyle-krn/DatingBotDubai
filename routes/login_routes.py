from fastapi import APIRouter, Response
from fastapi import Depends,status
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from data import config

security = HTTPBasic()

login_router = APIRouter()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """Верификация в админке"""
    correct_username = secrets.compare_digest(credentials.username, config.ADMIN_LOGIN)
    correct_password = secrets.compare_digest(credentials.password, config.ADMIN_PSW)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@login_router.get("/logout")
def get_headers(response: Response):
    response.delete_cookie("Authorization")
    return {"message": "Hello World"}

