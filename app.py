from fastapi import FastAPI
import asyncio
from main import deriv_price_stream

app = FastAPI()

@app.get("/")
def index():
    return {"message": "V75 Signal Bot is Running"}

@app.get("/run")
async def run_bot():
    await deriv_price_stream()
    return {"status": "Signal evaluated"}
