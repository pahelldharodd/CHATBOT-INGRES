"""
ML Prediction Service for Groundwater Depletion Analysis
Provides advanced machine learning predictions for groundwater sustainability
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from pathlib import Path

# Prediction request models
class PredictionRequest(BaseModel):
    state: str
    district: str
    years_ahead: Optional[int] = 20

class AlertThresholds(BaseModel):
    critical_extraction: float = 85.0
    high_extraction: float = 70.0
    medium_extraction: float = 50.0
    rapid_growth_rate: float = 2.0
    critical_years_left: int = 10

@dataclass
class PredictionResult:
    location: str
    current_extraction_rate: float
    predicted_depletion_year: Optional[int]
    years_left: Optional[int]
    risk_level: str
    risk_color: str
    time_series_data: List[Dict]
    alerts: List[Dict]
    summary: Dict[str, Any]

class GroundwaterMLPredictor:
    def __init__(self):
        self.alert_thresholds = AlertThresholds()
        
    def load_historical_data(self, state: str, district: str) -> pd.DataFrame:
        """
        Load historical groundwater data for the specified location
        In a real implementation, this would connect to your database
        """
        # Mock historical data generation for demonstration
        current_year = datetime.now().year
        years = list(range(current_year - 10, current_year + 1))
        
        # Simulate realistic groundwater patterns based on location
        base_extraction = self._get_base_extraction_rate(state, district)
        base_recharge = self._get_base_recharge_rate(state, district)
        
        data = []
        for i, year in enumerate(years):
            # Add trend and noise
            trend_factor = i / len(years)
            extraction = base_extraction + (trend_factor * 20) + np.random.normal(0, 3)
            recharge = base_recharge - (trend_factor * 10) + np.random.normal(0, 2)
            
            # Keep within realistic bounds
            extraction = max(10, min(95, extraction))
            recharge = max(5, min(60, recharge))
            
            data.append({
                'year': year,
                'extraction_rate': round(extraction, 2),
                'recharge_rate': round(recharge, 2),
                'net_depletion': round(extraction - recharge, 2),
                'groundwater_level': round(100 - extraction + recharge, 2)
            })
        
        return pd.DataFrame(data)
    
    def _get_base_extraction_rate(self, state: str, district: str) -> float:
        """Get base extraction rate based on location characteristics"""
        # High extraction states (agriculture intensive)
        high_extraction_states = ['PUNJAB', 'HARYANA', 'RAJASTHAN', 'GUJARAT']
        medium_extraction_states = ['MAHARASHTRA', 'UTTAR PRADESH', 'MADHYA PRADESH']
        
        if state in high_extraction_states:
            return np.random.uniform(60, 80)
        elif state in medium_extraction_states:
            return np.random.uniform(40, 60)
        else:
            return np.random.uniform(25, 45)
    
    def _get_base_recharge_rate(self, state: str, district: str) -> float:
        """Get base recharge rate based on location characteristics"""
        # High rainfall states
        high_rainfall_states = ['KERALA', 'KARNATAKA', 'WEST BENGAL', 'ASSAM']
        medium_rainfall_states = ['MAHARASHTRA', 'ANDHRA PRADESH', 'TAMIL NADU']
        
        if state in high_rainfall_states:
            return np.random.uniform(35, 50)
        elif state in medium_rainfall_states:
            return np.random.uniform(25, 40)
        else:
            return np.random.uniform(15, 30)
    
    def predict_future_trends(self, historical_data: pd.DataFrame, years_ahead: int = 20) -> pd.DataFrame:
        """
        Predict future groundwater trends using trend analysis
        In a real implementation, this would use sophisticated ML models
        """
        # Calculate trends from historical data
        extraction_trend = np.polyfit(historical_data['year'], historical_data['extraction_rate'], 1)[0]
        recharge_trend = np.polyfit(historical_data['year'], historical_data['recharge_rate'], 1)[0]
        
        # Generate future predictions
        last_year = historical_data['year'].max()
        last_extraction = historical_data['extraction_rate'].iloc[-1]
        last_recharge = historical_data['recharge_rate'].iloc[-1]
        
        future_data = []
        for i in range(1, years_ahead + 1):
            future_year = last_year + i
            
            # Apply trends with some acceleration/deceleration
            acceleration_factor = 1 + (i * 0.02)  # Slight acceleration
            future_extraction = last_extraction + (extraction_trend * i * acceleration_factor)
            future_recharge = last_recharge + (recharge_trend * i * 0.8)  # Recharge degrades slower
            
            # Add some randomness but keep trends
            future_extraction += np.random.normal(0, 1)
            future_recharge += np.random.normal(0, 0.5)
            
            # Keep within bounds
            future_extraction = max(10, min(98, future_extraction))
            future_recharge = max(2, min(50, future_recharge))
            
            future_data.append({
                'year': future_year,
                'extraction_rate': round(future_extraction, 2),
                'recharge_rate': round(future_recharge, 2),
                'net_depletion': round(future_extraction - future_recharge, 2),
                'groundwater_level': round(100 - future_extraction + future_recharge, 2),
                'type': 'prediction'
            })
        
        return pd.DataFrame(future_data)
    
    def calculate_depletion_timeline(self, combined_data: pd.DataFrame) -> tuple:
        """Calculate when complete depletion might occur"""
        future_data = combined_data[combined_data.get('type') == 'prediction']
        
        # Find when extraction rate reaches critical levels (>90%)
        critical_rows = future_data[future_data['extraction_rate'] >= 90]
        
        if not critical_rows.empty:
            depletion_year = critical_rows.iloc[0]['year']
            current_year = datetime.now().year
            years_left = depletion_year - current_year
            return int(depletion_year), int(years_left)
        
        return None, None
    
    def assess_risk_level(self, current_extraction: float, trend: float) -> tuple:
        """Assess current risk level and assign color"""
        risk_color_map = {
            'Low': '#10b981',
            'Medium': '#f59e0b', 
            'High': '#ef4444',
            'Critical': '#dc2626'
        }
        
        if current_extraction >= 85:
            risk_level = 'Critical'
        elif current_extraction >= 70:
            risk_level = 'High'
        elif current_extraction >= 50:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Upgrade risk if trend is rapidly increasing
        if trend > 3 and risk_level != 'Critical':
            risk_levels = ['Low', 'Medium', 'High', 'Critical']
            current_index = risk_levels.index(risk_level)
            risk_level = risk_levels[min(current_index + 1, len(risk_levels) - 1)]
        
        return risk_level, risk_color_map[risk_level]
    
    def generate_alerts(self, historical_data: pd.DataFrame, current_extraction: float, 
                       trend: float, years_left: Optional[int]) -> List[Dict]:
        """Generate alerts based on current conditions and trends"""
        alerts = []
        
        # Critical extraction rate alert
        if current_extraction >= self.alert_thresholds.critical_extraction:
            alerts.append({
                'type': 'critical',
                'priority': 'critical',
                'message': f'CRITICAL: Extraction rate at {current_extraction:.1f}% - Immediate action required',
                'icon': '🚨'
            })
        elif current_extraction >= self.alert_thresholds.high_extraction:
            alerts.append({
                'type': 'warning',
                'priority': 'high',
                'message': f'WARNING: High extraction rate at {current_extraction:.1f}% - Monitor closely',
                'icon': '⚠️'
            })
        
        # Rapid growth trend alert
        if trend >= self.alert_thresholds.rapid_growth_rate:
            alerts.append({
                'type': 'trend',
                'priority': 'high',
                'message': f'ALERT: Extraction rate increasing by {trend:.1f}% annually - Unsustainable trend',
                'icon': '📈'
            })
        
        # Depletion timeline alert
        if years_left and years_left <= self.alert_thresholds.critical_years_left:
            alerts.append({
                'type': 'depletion',
                'priority': 'critical',
                'message': f'URGENT: Complete depletion predicted in {years_left} years',
                'icon': '⏰'
            })
        
        # Sustainability alerts
        latest_data = historical_data.iloc[-1]
        if latest_data['net_depletion'] > 30:
            alerts.append({
                'type': 'sustainability',
                'priority': 'medium',
                'message': f'Net depletion rate of {latest_data["net_depletion"]:.1f}% exceeds sustainable levels',
                'icon': '💧'
            })
        
        return alerts
    
    def generate_prediction(self, state: str, district: str, years_ahead: int = 20) -> PredictionResult:
        """Generate comprehensive prediction for the specified location"""
        location = f"{district}, {state}"
        
        # Load historical data
        historical_data = self.load_historical_data(state, district)
        
        # Generate predictions
        future_data = self.predict_future_trends(historical_data, years_ahead)
        
        # Combine historical and future data
        historical_data['type'] = 'historical'
        combined_data = pd.concat([historical_data, future_data], ignore_index=True)
        
        # Calculate metrics
        current_extraction = historical_data['extraction_rate'].iloc[-1]
        extraction_trend = np.polyfit(historical_data['year'], historical_data['extraction_rate'], 1)[0]
        
        # Assessment
        depletion_year, years_left = self.calculate_depletion_timeline(combined_data)
        risk_level, risk_color = self.assess_risk_level(current_extraction, extraction_trend)
        alerts = self.generate_alerts(historical_data, current_extraction, extraction_trend, years_left)
        
        # Prepare time series data
        time_series_data = combined_data.to_dict('records')
        
        # Summary statistics
        summary = {
            'current_extraction_rate': round(current_extraction, 2),
            'average_recharge_rate': round(historical_data['recharge_rate'].mean(), 2),
            'net_depletion_rate': round(historical_data['net_depletion'].iloc[-1], 2),
            'extraction_trend': round(extraction_trend, 2),
            'trend_direction': 'Increasing' if extraction_trend > 0 else 'Decreasing',
            'sustainability_index': round(max(0, 100 - current_extraction), 2)
        }
        
        return PredictionResult(
            location=location,
            current_extraction_rate=round(current_extraction, 2),
            predicted_depletion_year=depletion_year,
            years_left=years_left,
            risk_level=risk_level,
            risk_color=risk_color,
            time_series_data=time_series_data,
            alerts=alerts,
            summary=summary
        )

# Initialize FastAPI app
prediction_app = FastAPI(title="Groundwater Prediction Service")

# CORS configuration
prediction_app.add_middleware(
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

# Initialize ML predictor
ml_predictor = GroundwaterMLPredictor()

@prediction_app.get("/prediction/health")
def health_check():
    return {"status": "healthy", "service": "groundwater-prediction"}

@prediction_app.post("/prediction/analyze")
def predict_groundwater_depletion(request: PredictionRequest):
    """
    Generate ML-powered groundwater depletion predictions
    """
    try:
        # Validate input
        if not request.state or not request.district:
            raise HTTPException(status_code=400, detail="State and district are required")
        
        if request.years_ahead and (request.years_ahead < 1 or request.years_ahead > 50):
            raise HTTPException(status_code=400, detail="Years ahead must be between 1 and 50")
        
        # Generate prediction
        result = ml_predictor.generate_prediction(
            state=request.state.upper(),
            district=request.district,
            years_ahead=request.years_ahead or 20
        )
        
        # Convert to dictionary for JSON response
        return {
            "location": result.location,
            "current_extraction_rate": result.current_extraction_rate,
            "predicted_depletion_year": result.predicted_depletion_year,
            "years_left": result.years_left,
            "risk_level": result.risk_level,
            "risk_color": result.risk_color,
            "time_series_data": result.time_series_data,
            "alerts": result.alerts,
            "summary": result.summary,
            "generated_at": datetime.now().isoformat(),
            "model_version": "1.0.0"
        }
        
    except Exception as e:
        print(f"[prediction_error] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@prediction_app.get("/prediction/locations")
def get_available_locations():
    """Get list of available states and districts for prediction"""
    states_districts = {
        "ANDHRA PRADESH": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool"],
        "GUJARAT": ["Ahmedabad", "Rajkot", "Surat", "Vadodara", "Jamnagar", "Junagadh"],
        "MAHARASHTRA": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur"],
        "PUNJAB": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
        "RAJASTHAN": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur"],
        "TAMIL NADU": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"]
    }
    
    return {
        "states": list(states_districts.keys()),
        "districts": states_districts,
        "total_locations": sum(len(districts) for districts in states_districts.values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(prediction_app, host="0.0.0.0", port=7862)