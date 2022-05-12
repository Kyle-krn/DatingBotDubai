from fastapi import APIRouter, Request, Response
from loader import templates
from fastapi import Depends,status # Assuming you have the FastAPI class for routing
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm


login_router = APIRouter()


import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "stanleyjobson")
    correct_password = secrets.compare_digest(credentials.password, "swordfish")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@login_router.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}



@login_router.get("/logout")
def get_headers(response: Response):
    response.delete_cookie("Authorization")
    return {"message": "Hello World"}

from starlette.datastructures import MutableHeaders
from fastapi import Request    

@login_router.get("/test")
def test(request: Request):
     new_header = MutableHeaders(request._headers)
     new_header["xxxxx"]="XXXXX"
     request._headers = new_header
     print(request.headers)
     return {}