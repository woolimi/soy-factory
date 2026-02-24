from fastapi import FastAPI

app = FastAPI(title="SoyServer")


@app.get("/")
def root():
    return {"service": "SoyServer", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
