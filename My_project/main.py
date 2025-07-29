from fastapi import FastAPI
import authentication as authentication
import publisher as publisher
import userlogin as userlogin

app = FastAPI()

app.include_router(userlogin.router)
app.include_router(authentication.router)
app.include_router(publisher.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)