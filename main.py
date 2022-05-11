
import uvicorn
from loader import app
from fastapi.staticfiles import StaticFiles
import routes

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes.event_router)
app.include_router(routes.user_router)
app.include_router(routes.login_router)

    

    


if __name__ == '__main__':
      uvicorn.run(app, port=8009, log_config=None)
      