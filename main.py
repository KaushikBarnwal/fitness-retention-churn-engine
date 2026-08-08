from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import uvicorn

app = FastAPI(
    title = "Retention Engine API",
    description = "ML microservice for predicting fitness churn risk.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to match your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "churn_production_model.pkl")
model = joblib.load(MODEL_PATH)

class MemberData(BaseModel):
    Near_Location: int
    Partner: int
    Promo_friends: int
    Contract_period: int
    Group_visits: int
    Age: int
    Avg_additional_charges_total: float
    Month_to_end_contract: float
    Lifetime: int
    Avg_class_frequency_total: float
    Avg_class_frequency_current_month: float
    
@app.get("/")
def read_root():
    return {"status": "online", "message": "Fitness Retention & Churn Engine API"}

@app.post("/api/predict-churn/")
def predict_churn(member: MemberData):
    data = member.model_dump()
    df = pd.DataFrame([data])
    df['freq_drop_off'] = df['Avg_class_frequency_current_month'] - df['Avg_class_frequency_total']
    df['charges_per_month'] = df['Avg_additional_charges_total'] / (df['Lifetime'] + 1)
    expected_columns = [
        'Near_Location', 'Partner', 'Promo_friends', 'Contract_period', 
        'Group_visits', 'Age', 'Avg_additional_charges_total', 'Month_to_end_contract', 
        'Lifetime', 'Avg_class_frequency_total', 'Avg_class_frequency_current_month',
        'freq_drop_off', 'charges_per_month'
    ]
    df = df[expected_columns]
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]
    
    if prediction == 1:
        if probability > 0.85:
            action = "Immediate 1:1 'Motivation Check-in' Call from Head Trainer"
        elif probability > 0.6:
            action = "Offer 2 Free Guest Passes for Friends"
        else:
            action = "Send 'We Miss You' Discounted Membership Email"
    else:
        action = "No Action Needed"
    return {
        "churn_risk": "HIGH" if prediction == 1 else "LOW",
        "probability_score": f"{round(probability * 100, 2)}%",
        "recommended_action": action
    }
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 