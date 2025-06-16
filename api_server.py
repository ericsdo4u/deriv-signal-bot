# # api_server.py

# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# import csv
# import os

# app = FastAPI()
# LOG_FILE = "signal_log.csv"

# @app.get("/")
# def read_root():
#     return {"message": "🚀 V75 Signal API is live."}

# @app.get("/latest-signal")
# def get_latest_signal():
#     if not os.path.exists(LOG_FILE):
#         return JSONResponse(status_code=404, content={"error": "No signal log found"})

#     try:
#         with open(LOG_FILE, mode='r') as file:
#             reader = list(csv.DictReader(file))
#             if not reader:
#                 return JSONResponse(status_code=404, content={"error": "Signal log is empty"})
#             latest = reader[-1]
#             return {"latest_signal": latest}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})

