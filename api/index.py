import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import numpy as np

# Load sample telemetry (replace with your actual data file path if needed)
with open("q-vercel-latency.json") as f:
    telemetry_data = json.load(f)

# FastAPI app
app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Pydantic model for request
class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

# POST endpoint
@app.post("/latency")
def check_latency(payload: LatencyRequest):
    regions = payload.regions
    threshold = payload.threshold_ms

    response: Dict[str, Dict] = {}

    for region in regions:
        # Filter telemetry by region
        region_data = [rec for rec in telemetry_data if rec["region"] == region]
        if not region_data:
            continue

        latencies = [rec["latency_ms"] for rec in region_data]
        uptimes = [rec["uptime"] for rec in region_data]

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    if not response:
        raise HTTPException(status_code=404, detail="No data for requested regions")

    return response
