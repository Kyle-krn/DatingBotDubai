from fastapi import APIRouter, Request, Response
from loader import templates
from fastapi import Depends,status # Assuming you have the FastAPI class for routing
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm


login_router = APIRouter()


# DB = {"username":{"password":"qwertyuiop"}} # unhashed

# @manager.user_loader
# def load_user(username:str):
#     user = DB.get(username)
#     return user

# @login_router.post("/auth/login")
# def login(data: OAuth2PasswordRequestForm = Depends()):
#     username = data.username
#     password = data.password
#     user = load_user(username)
#     if not user:
#         return RedirectResponse(url="/login",status_code=status.HTTP_302_FOUND)
#     elif password != user['password']:
#         return RedirectResponse(url="/login",status_code=status.HTTP_302_FOUND)
#     access_token = manager.create_access_token(
#         data={"sub":username}
#     )
#     resp = RedirectResponse(url="/",status_code=status.HTTP_302_FOUND)
#     manager.set_cookie(resp,access_token)
#     return resp

# @login_router.get("/private")
# def getPrivateendpoint(_=Depends(manager)):
#     return "You are an authentciated user"

# @login_router.get("/login",response_class=HTMLResponse)
# def loginwithCreds(request:Request):
#     return templates.TemplateResponse("login.html", {"request": request})
    
# # @app.get("/logout")
# # def logout(response : Response):
# #   response = RedirectResponse('/login', status_code= 302)
# #   response.delete_cookie(key ='auth')
# #   return response
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