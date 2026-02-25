import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.pc_bridge import start as bridge_start, stop as bridge_stop

# RFID/시리얼/TCP 브릿지 디버깅용 로그 출력
logging.getLogger("app").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bridge_start()
    try:
        yield
    finally:
        bridge_stop()


app = FastAPI(title="SoyServer", lifespan=lifespan)


@app.get("/")
def root():
    return {"service": "SoyServer", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
