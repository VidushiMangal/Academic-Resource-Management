from fastapi import FastAPI
import login
import publisher

app = FastAPI()

app.include_router(login.router)
app.include_router(publisher.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)