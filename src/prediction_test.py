"""
Simple test version of the ML Prediction Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import random

# Prediction request model
class PredictionRequest(BaseModel):
    state: str
    district: str
    years_ahead: int = 20

# Initialize FastAPI app
app = FastAPI(title="Groundwater Prediction Service - Test")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/prediction/health")
def health_check():
    return {"status": "healthy", "service": "groundwater-prediction-test"}

@app.post("/prediction/analyze")
def predict_groundwater_depletion(request: PredictionRequest):
    """
    Generate test groundwater depletion predictions
    """
    try:
        print(f"Received prediction request for {request.state}, {request.district}")
        
        # Generate mock time series data
        current_year = datetime.now().year
        time_series_data = []
        
        # Historical data (last 10 years)
        base_extraction = random.uniform(40, 80)
        base_recharge = random.uniform(20, 40)
        
        for i in range(-10, request.years_ahead + 1):
            year = current_year + i
            extraction = base_extraction + (i * 1.5) + random.uniform(-5, 5)
            recharge = base_recharge - (i * 0.5) + random.uniform(-2, 2)
            
            extraction = max(10, min(95, extraction))
            recharge = max(5, min(50, recharge))
            
            time_series_data.append({
                "year": year,
                "extraction_rate": round(extraction, 2),
                "recharge_rate": round(recharge, 2),
                "net_depletion": round(extraction - recharge, 2),
                "type": "historical" if i <= 0 else "prediction"
            })
        
        current_extraction = time_series_data[10]["extraction_rate"]  # Current year data
        
        # Determine risk level
        if current_extraction >= 85:
            risk_level = "Critical"
            risk_color = "#dc2626"
        elif current_extraction >= 70:
            risk_level = "High"
            risk_color = "#ef4444"
        elif current_extraction >= 50:
            risk_level = "Medium"
            risk_color = "#f59e0b"
        else:
            risk_level = "Low"
            risk_color = "#10b981"
        
        # Generate alerts
        alerts = []
        if current_extraction >= 80:
            alerts.append({
                "type": "critical",
                "priority": "critical",
                "message": f"CRITICAL: Extraction rate at {current_extraction:.1f}% - Immediate action required",
                "icon": "🚨"
            })
        
        if current_extraction > 70:
            alerts.append({
                "type": "warning",
                "priority": "high", 
                "message": f"WARNING: High extraction rate detected",
                "icon": "⚠️"
            })
        
        # Find depletion year
        depletion_data = [d for d in time_series_data if d["extraction_rate"] >= 90]
        predicted_depletion_year = depletion_data[0]["year"] if depletion_data else None
        years_left = predicted_depletion_year - current_year if predicted_depletion_year else None
        
        response = {
            "location": f"{request.district}, {request.state}",
            "current_extraction_rate": current_extraction,
            "predicted_depletion_year": predicted_depletion_year,
            "years_left": years_left,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "time_series_data": time_series_data,
            "alerts": alerts,
            "summary": {
                "current_extraction_rate": current_extraction,
                "average_recharge_rate": base_recharge,
                "net_depletion_rate": current_extraction - base_recharge,
                "extraction_trend": 1.5,
                "trend_direction": "Increasing"
            },
            "generated_at": datetime.now().isoformat(),
            "model_version": "test-1.0.0"
        }
        
        print(f"Generated prediction response successfully")
        return response
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting test prediction service...")
    uvicorn.run(app, host="0.0.0.0", port=7862, log_level="info")